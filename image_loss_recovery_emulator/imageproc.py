import cv2
import numpy as np
import random
import os

np.random.seed(7)

# loss_rate = 0.2

def permute_pixels(image):
    t = image.shape
    row, col, d = image.shape
    out = np.copy(image)
    # out = np.transpose(out, [1, 2, 0])
    flat = np.ravel(out)
    ans = np.copy(flat)
    # ans = np.reshape(ans, (row, col, d))
    coords = np.random.permutation(len(flat) // 3)
    i = 0
    dic = {}
    for c in coords:
        ans[3 * c:3 * c + 3] = flat[3 * i:3 * i + 3]
        dic[c] = i
        i += 1

    ans = np.reshape(ans, (row, col, d))
    return ans, dic, row, col


def reconstruct_pixels(pic, dic, rr, cc, orig_mask):
    flat = np.ravel(pic)
    original = np.copy(flat)
    permuted_mask = []
    for pos in dic:
        original[3 * dic[pos]:3 * dic[pos] + 3] = flat[3 * int(pos): 3 * int(pos) + 3]
    for idx in orig_mask:
        permuted_mask.append(dic[idx])
    img = np.reshape(original, (rr, cc, 3))
    return img, permuted_mask


def random_loss(raw, ratio=0.0, chunk_size=150):
    raw_size = len(raw)
    padded_size = (raw_size // chunk_size) * chunk_size + chunk_size
    n_mask = int((padded_size // chunk_size) * float(ratio))
    n_block = padded_size // chunk_size
    mask = np.random.choice(n_block, size=n_mask, replace=False)
    raw = bytearray(raw)
    raw += bytearray(padded_size - raw_size)
    for masked_idx in mask:
        start_idx = masked_idx * chunk_size
        raw[start_idx:start_idx + chunk_size] = bytearray(chunk_size)
    return (bytes(raw[:-(padded_size - raw_size)]), mask)


def apply_loss_to_img(src_img, loss_rate, chunk_size=150):
    img_str = cv2.imencode('.bmp', src_img)[1].tostring()
    pixel_arr_offset = int('A', base=16)
    p = img_str[pixel_arr_offset:pixel_arr_offset + 4]
    offset = int.from_bytes(p, byteorder='little')
    data_seg = img_str[offset:]
    lost_img_str, mask = random_loss(data_seg, loss_rate, chunk_size)
    whole_str = img_str[:offset] + lost_img_str
    nparr = np.fromstring(whole_str, np.uint8)
    im = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
    return im, mask


def random_loss_points(s, ratio=0.0):
    t = bytearray(s)
    l = len(t)
    num_pepper = np.ceil(len(s) * ratio)
    coords = np.random.randint(0, l - 1, int(num_pepper))
    for ind in coords:
        t[ind:ind + 1] = bytearray(1)
    return bytes(t)


def display_result(img, title='Image', show=1):
    cv2.imshow(title, img)
    # Required to show and close the image window
    if show == 1:
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def recover(img, mask, chunk_size):
    # indices = np.where(img == [0])
    row, col, d = img.shape
    z = np.zeros((row, col), dtype=np.uint8)
    z = np.ravel(z)
    for masked_idx in mask:
        start_idx = masked_idx * chunk_size
        z[start_idx:start_idx + chunk_size] = 1
    z = np.reshape(z, (row, col))

    dst = cv2.inpaint(img, z, 7, cv2.INPAINT_TELEA)
    dst = cv2.medianBlur(dst, 7)
    dst = cv2.inpaint(dst, z, 5, cv2.INPAINT_TELEA)
    dst = cv2.medianBlur(dst, 5)

    return dst

def create_damaged_images_set(filename, loss_rate, redo=True):
    orig_name = os.path.splitext(filename)[0]
    lr = str(int(loss_rate * 100))
    orig_name = orig_name + '_' + lr
    raw_img_name = orig_name + '_0.bmp'
    lossy_img_name = orig_name + '_1.bmp'
    lossy_and_repaired_name = orig_name + '_2.bmp'
    inter_deinter_name = orig_name + '_3.bmp'
    inter_deinter_repaired_name = orig_name + '_4.bmp'

    if not redo:
        exists = os.path.isfile(raw_img_name)
        exists = exists and os.path.isfile(lossy_img_name)
        exists = exists and os.path.isfile(lossy_and_repaired_name)
        exists = exists and os.path.isfile(inter_deinter_name)
        exists = exists and os.path.isfile(inter_deinter_repaired_name)
        if (exists):
            return

    image = cv2.imread(filename, cv2.IMREAD_COLOR)

    cv2.imwrite(raw_img_name, image)

    shortName = filename.split('.')[0]
    original_scheme, mask = apply_loss_to_img(image, loss_rate, chunk_size=150)
    # display_result(original_scheme)
    cv2.imwrite(lossy_img_name, original_scheme)

    # try_repaired = cv2.medianBlur(original_scheme, 5)
    try_repaired = recover(original_scheme, mask, chunk_size=150)

    cv2.imwrite(lossy_and_repaired_name, try_repaired)

    (perm_img, d, row, col) = permute_pixels(image)
    # cv2.imwrite(shortName + '_interleaved' + '.bmp', perm_img)

    dmg_permuted_img, mask = apply_loss_to_img(perm_img, loss_rate, chunk_size=150)
    # cv2.imwrite(shortName + '_interleaved_then_with_loss' + '.bmp', dmg_permuted_img)

    reconstructed, reconstructed_mask = reconstruct_pixels(dmg_permuted_img, d, row, col, mask)
    cv2.imwrite(inter_deinter_name, reconstructed)

    # repaired = cv2.medianBlur(reconstructed, 5)
    repaired = recover(reconstructed, reconstructed_mask, chunk_size=150)

    cv2.imwrite(inter_deinter_repaired_name, repaired)

# Py3
import vifp
import ssim
import psnr
import niqe
import reco
from image_loss_recovery_emulator.imageproc import create_damaged_images_set
import pickle
import matplotlib.pyplot as plt
import scipy
import numpy

file_list = ["airplane", "automobile", "bird", "cat", "deer",
             "dog", "frog", "horse", "ship", "truck"]
# loss_rate_list = [0.02, 0.04, 0.06, 0.08, 0.10, 0.2, 0.3]
loss_rate_list = [0.02, 0.04, 0.06, 0.08, 0.10, 0.2, 0.3, 0.4]
quality_metric_list = ["vifp", "psnr", "ssim"]

# use numpy array to get three quality
def image_np_to_quality(ref, dist,
                        use_vifp = True, use_ssim = True,
                        use_psnr = True, use_niqe = False,
                        use_reco = False):
    result = {}
    if (use_vifp):
        result["vifp"] = vifp.vifp_mscale(ref, dist)

    if (use_ssim):
        result["ssim"] = ssim.ssim_exact(ref/255, dist/255)

    if (use_psnr):
        result["psnr"] = psnr.psnr(ref, dist)/100

    if (use_niqe):
        result["niqe"] = niqe.niqe(dist/255)

    if (use_reco):
        result["reco"] = reco.reco(ref/255, dist/255)
    return result

# use ref and dist filename to get image quality indexes
def image_file_to_quality(ref_filename, dist_filename):
    ref = scipy.misc.imread(ref_filename, flatten=True).astype(numpy.float32)
    dist = scipy.misc.imread(dist_filename, flatten=True).astype(numpy.float32)

    result = image_np_to_quality(ref, dist)
    print(result)

def ref_and_dist_list_to_quality_list(ref, dist_list):
    result_list = []
    for dist in dist_list:
        result = image_np_to_quality(ref, dist)
        result_list.append(result)

    return result_list

def one_name_to_all_result(name):
    ref_filename = name + "_0.bmp"
    dist_filename_list = [name + "_" + n + ".bmp" for n in["1", "2", "3", "4"]]
    ref = scipy.misc.imread(ref_filename, flatten=True).astype(numpy.float32)
    dist_list = [scipy.misc.imread(dist_filename, flatten=True).astype(numpy.float32) for dist_filename in dist_filename_list]
    return ref_and_dist_list_to_quality_list(ref, dist_list)


# generate file_lr_id.bmp, lr in loss rate list, id in [0,5]
def emulator_file_list_at_all_loss_rate(path, file_list, loss_rate_list):
    for loss_rate in loss_rate_list:
        for filename in file_list:
            # todo: need to check the existence of the files
            create_damaged_images_set(path+filename+".bmp", loss_rate, redo=False) # loss rate here is a float

# get 1,2,3,4 results, for filename_string of loss rate
def get_result_for_one_file_at_loss_rate(filename, loss_rate):
    # convert loss rate to string
    loss_rate_str = str(int(loss_rate*100))
    name = filename + "_" + loss_rate_str
    return one_name_to_all_result(name)


# data looks like
# {"10":{"cute_dog":[{"vifp":0.2, "psnr":0.3, "ssim":0.4}, ..., ..., ...], "xxx":[...]},
#  "20":...}

def get_all_result(path, file_list, loss_rate_list):
    dataset_result = {}
    for loss_rate in loss_rate_list:
        loss_rate_result = {}
        for filename in file_list:
            filename = path + filename
            loss_rate_result[filename] = get_result_for_one_file_at_loss_rate(filename, loss_rate)
        # loss_rate_str = str(int(loss_rate*100))
        dataset_result[loss_rate] = loss_rate_result

    pickle.dump(dataset_result, open('data.pkl', 'wb'))
    return dataset_result

def parse_dataset_result_for_one_metric(dataset_result, metric):
    loss_rate_list = []
    loss_list = []
    loss_fix_list = []
    interleave_list = []
    interleave_fix_list = []

    for loss_rate, lr_result in dataset_result.items():
        value0_list = []
        value1_list = []
        value2_list = []
        value3_list = []
        # get average quality for all files under one loss rate
        for filename, result in lr_result.items():
            value0_list.append(result[0][metric]) # loss
            value1_list.append(result[1][metric])
            value2_list.append(result[2][metric]) # interleave
            value3_list.append(result[3][metric])

        loss_list.append(sum(value0_list) / len(value0_list))
        loss_fix_list.append(sum(value1_list) / len(value1_list))
        interleave_list.append(sum(value2_list) / len(value2_list))
        interleave_fix_list.append(sum(value3_list) / len(value3_list))
        loss_rate_list.append(loss_rate)

    plt.plot(loss_rate_list, loss_list, label="Loss without recover")
    plt.plot(loss_rate_list, loss_fix_list, label="Loss with recover")
    plt.plot(loss_rate_list, interleave_list, label="Interleave without recover")
    plt.plot(loss_rate_list, interleave_fix_list, label="Interleave with recover")

    plt.legend(loc='upper right')
    plt.xlabel('Loss Rate')
    plt.ylabel('Metric')
    plt.savefig('quality_vs_loss_rate_'+metric+'.png')
    plt.gcf().clear()

print("Emulating all files")
emulator_file_list_at_all_loss_rate("./testset/", file_list, loss_rate_list)

print("Getting results")
dataset_result = get_all_result("./testset/", file_list, loss_rate_list)

print("Generating plots")
parse_dataset_result_for_one_metric(dataset_result, 'vifp')
parse_dataset_result_for_one_metric(dataset_result, 'psnr')
parse_dataset_result_for_one_metric(dataset_result, 'ssim')

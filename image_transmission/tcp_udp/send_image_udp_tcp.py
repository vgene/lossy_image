import socket
import sys
import struct
import random
import traceback

# X, Y, Z; For the first X (percent) of packets,
# a meta packet in every Y packets,
# then sending Z EOF packet.
X = 0.2
Y = 10
Z = 5

META_TYPE =0
DATA_TYPE =1
EOF_TYPE = 2

image_filename = "./cute_dog.bmp" # @TODO: change this
CHUNK_SIZE = 512 # @TODO: change this

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('10.0.2.2', 20008)
#server_address = ('127.0.0.1', 20008)

# Get size, offset, then split into all meta(fileheader, DIB, Color-table) and all data
def get_bmp_meta_and_data(bmp_filename):
    bmp = open(bmp_filename, 'rb')
    # print('Type:', bmp.read(2).decode())
    # print('Size: %s' % struct.unpack('I', bmp.read(4)))
    # print('Reserved 1: %s' % struct.unpack('H', bmp.read(2)))
    # print('Reserved 2: %s' % struct.unpack('H', bmp.read(2)))

    bmp.seek(2, 1) # relative
    size = struct.unpack('I', bmp.read(4))[0]
    bmp.seek(4, 1) # relative
    offset = struct.unpack('I', bmp.read(4))[0]

    bmp.seek(0, 0) # from start
    meta = bmp.read(offset)
    data = bmp.read()
    bmp.close()

    return meta, data

img_meta, img_data = get_bmp_meta_and_data(image_filename)
data_size = len(img_data)
chunk_cnt = (data_size // CHUNK_SIZE) + ((data_size % CHUNK_SIZE) > 0)
last_size = data_size - (chunk_cnt - 1) * CHUNK_SIZE

seq_X = int(chunk_cnt * X)

# send packets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# get random identifier
rand_identifier = random.randint(1,1000000)

# send meta
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('10.0.2.2', 20008)


print("Start sending image")
try:
    # send data and meta
    seq = 0
    p_cnt = 0
    while seq < chunk_cnt:
        # send packets
        if seq < seq_X and p_cnt % Y == 0:
            # send meta
            meta = struct.pack(">LLLLL", META_TYPE, rand_identifier, chunk_cnt, CHUNK_SIZE, last_size)
            meta = meta + img_meta
            sock.sendto(meta, server_address)
            p_cnt += 1
        else:
            # send data
            data = struct.pack(">LLL", DATA_TYPE, rand_identifier, seq)
            # check if it is last packet
            if seq == chunk_cnt - 1:
                data = data + img_data[CHUNK_SIZE*seq :]
            else:
                data = data + img_data[CHUNK_SIZE*seq : CHUNK_SIZE*(seq+1)]
            seq += 1
            p_cnt += 1
            sock.sendto(data, server_address)
    # send EOF
    for i in range(0, Z):
        eof = struct.pack(">LL", EOF_TYPE, rand_identifier)
        sock.sendto(eof, server_address)

except Exception as e:
    print("Something is wrong")
    traceback.print_exc()
finally:
    sock.close()
print("Finish sending image")


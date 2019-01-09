import socket
import sys
import struct
import traceback

# X, Y, Z; For the first X (percent) of packets,
# a meta packet in every Y packets,
# then sending Z EOF packet.
X = 0.2
Y = 10
Z = 10

META_TYPE = 0
DATA_TYPE = 1
EOF_TYPE = 2

image_filename = "./cute_dog.bmp" # @TODO: change this
chunk_size = 4096 # @TODO: change this

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

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('10.0.2.2', 20008)

img_meta, img_data = get_bmp_meta_and_data(image_filename)
data_size = len(data)
dp_cnt = (data_size // buffer_size) + ((data_size % buffer_size) > 0)

seq_X = dp_cnt * X

# send packets
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# get random identifier
rand_identifier = 2123 # @TODO: change this
try:
    # send data and meta
    seq = 0
    while seq < dp_cnt:
        # send packets
        if seq < seq_X and seq % Y == 0: # if
            # send meta
            meta = struct.pack(">cLL", META_TYPE, rand_identifier, dp_cnt)
            meta = meta + img_meta
            sock.sendto(meta, server_address)
        else:
            # send data
            data = struct.pack(">cL", DATA_TYPE, rand_identifier)
            # check if it is last packet
            if seq == dp_cnt - 1:
                data = data + img_data[chunk_size*seq :]
            else:
                data = data + img_data[chunk_size*seq : chunk_size*(seq+1)]
            seq += 1
            sock.sendto(meta, server_address)
    # send EOF
    for i in range(0, Z):
        eof = struct.pack(">cL", EOF_TYPE, rand_identifier)
        sock.sendto(meta, server_address)

except Exception as e:
    print("Something is wrong")
    traceback.print_exc()
finally:
    sock.close()

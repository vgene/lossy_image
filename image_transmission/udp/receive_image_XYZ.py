import socket
import sys
import time
import struct
import traceback

# To be done:
# need to add active file retirement policy

META_TYPE = 0
DATA_TYPE = 1
EOF_TYPE = 2

BUFFER_SIZE = 8192
MAX_TIMEOUT = 2000 # timeout in ms
ON_THE_FLY_THRES = 100
# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('127.0.0.1', 20008)
print('starting UDP up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
# sock.listen(1)

def write_to_file(data, filename="cute_dog_save.bmp"):
    f = open(filename, "wb")
    f.write(data)
    f.close()

active_files = dict()
start_time = 0

def decode_and_reorder(packet):
    # 0-3 packet_type
    # 4-7 rand_id
    # * if meta
    #   8-11 chunk_cnt
    #   12-15 chunk_size
    #   16-19 last_chunk_size
    #   20- bmp_meta_data
    # * if data
    #   9-11 seq
    #   12- img_data
    def get_and_delete_file(rand_id):
        # Get time and calculate integrity
        if active_files[rand_id][-1] == 0:
            global start_time
            print("--- Finished in {0:.4f} seconds, data integrity is {1:.4f}---"
                .format(time.time() - start_time, 1.0 - (active_files[rand_id][1] / active_files[rand_id][3])))
            file = active_files[rand_id][2] + b''.join(active_files[rand_id][0]) # combine img meta and data
            active_files[rand_id][-1] = 1
            # del active_files[rand_id]
            return file
        else:
            return None

    def put_meta_in_dict(rand_id, packet):
        global start_time
        start_time = time.time()
        chunk_cnt = struct.unpack(">L", packet[8:12])[0]
        chunk_size = struct.unpack(">L", packet[12:16])[0]
        last_size = struct.unpack(">L", packet[16:20])[0]
        img_meta = packet[20:]
        if (chunk_size > 50000 or chunk_cnt > 50000):
            print("Bad meta; Abandon!")

        img_data = [bytearray([0] * chunk_size)] * (chunk_cnt-1) + [bytearray([0]*last_size)] # create an empty data
        remain_cnt = chunk_cnt
        done = 0
        active_files[rand_id] = [img_data, remain_cnt, img_meta, chunk_cnt, chunk_size, last_size, done]
        return None


    def put_data_in_dict(rand_id, packet):
        seq = struct.unpack(">L", packet[8:12])[0]
        active_files[rand_id][0][seq] = packet[12:] # put image chunk in place
        active_files[rand_id][1] -= 1 # decrease remain count

        if active_files[rand_id][1] == 0:
            return get_and_delete_file(rand_id)
        else:
            return None

    # get meta data
    ptype = struct.unpack(">L", packet[0:4])[0]
    rand_id = struct.unpack(">L", packet[4:8])[0]

    # if is meta data
    if ptype == META_TYPE:
        print("got meta")
        if rand_id in active_files:
            return None
        else:
            put_meta_in_dict(rand_id, packet)
            return None
    # if is data
    elif ptype == DATA_TYPE:
        print("got data")
        if rand_id not in active_files:
            print("Not in data")
            return None
        else:
            return put_data_in_dict(rand_id, packet)
    # if is EOF
    elif ptype == EOF_TYPE:
        print("got eof")
        if rand_id not in active_files:
            return None
        else:
            return get_and_delete_file(rand_id)
    # something is wrong!
    else:
        return None

while True:
    try:
        # Receive the data in small chunks and retransmit it
        data, address = sock.recvfrom(BUFFER_SIZE)
        file = decode_and_reorder(data)
        if file:
            write_to_file(file)
    except Exception as e:
        print(e)
        traceback.print_exc()

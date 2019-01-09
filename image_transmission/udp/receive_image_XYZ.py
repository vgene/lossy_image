import socket
import sys
import time
import struct

# X, Y, Z; For the first X% of packets,
# a meta packet in every Y packets,
# then sending Z EOF packet.

# UDP Header
# packet_type (i) |


MAX_TIMEOUT = 2000 # timeout in ms
X = 20
Y = 10
Z = 10
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

# UDP: total_packet_number(? bits) | interleave_protocol_number(2-3 bits) |
#      sequence_number(? bits) | rand_identifier (? bits) |
#      meta_data (? bits) | interleaved_data

active_set = set()
active_files = dict()
active_files_meta = dict() # file meta; total_packet_number | on_fly_packet_number

def buffer_and_reorder(packet):

    # get meta data
    struct_format = ">LLL"
    meta_len = 12 # rand_identifier(long)  | sequence_number(long)
    meta = packet[0:meta_len]
    data = packet[meta_len:]

    rand_identifier, total_packet_number, seq = struct.unpack(struct_format, meta)
    print(seq)

    if rand_identifier not in active_set:
        active_set.add(rand_identifier)
        active_files[rand_identifier] = [None]*total_packet_number # create a list to hold data
        active_files[rand_identifier][seq] = data
        active_files_meta[rand_identifier] = dict()
        active_files_meta[rand_identifier]['total_num'] = total_packet_number
        active_files_meta[rand_identifier]['on_fly_num'] = total_packet_number - 1
    else:
        active_files[rand_identifier][seq] = data
        active_files_meta[rand_identifier]['on_fly_num'] -= 1
        if (active_files_meta[rand_identifier]['on_fly_num'] == 0):
        # if (active_files_meta[rand_identifier]['on_fly_num'] < ON_THE_FLY_THRES):
            file = b''.join(active_files[rand_identifier])
            del active_files[rand_identifier]
            del active_files_meta[rand_identifier]
            active_set.remove(rand_identifier)
            return file
    return None

buffer_size = 8192
while True:
    try:
        # Receive the data in small chunks and retransmit it
        data, address = sock.recvfrom(buffer_size)
        start_time = time.time()
        file = buffer_and_reorder(data)
        if file:
            end_time = time.time()
            print("--- {0:.4f} seconds ---".format(time.time() - start_time))
            write_to_file(file)
            break
    except Exception as e:
        print(e)

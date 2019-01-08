import socket
import sys
import struct

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Connect the socket to the port where the server is listening
server_address = ('10.0.2.2', 20008)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
count = 0

image = "./cutedog.bmp"
fd = open(image, 'rb')
message = fd.read()
fd.close()
buffer_size = 4096
total_packet_number = (len(message) / buffer_size) + (len(message) % buffer_size > 0)

rand_identifier = 2123

for seq in range(0, p_cnt):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        meta = struct.pack(">LLL", rand_identifier,  total_packet_number, seq)
        if (seq == p_cnt - 1):
            sock.sendto(meta + message[seq * buffer_size:], server_address)
        else:
            sock.sendto(meta + message[seq * buffer: (seq+1) * buffer], address)

    except Exception as e:
        print("Something is wrong")
    finally:
        sock.close()
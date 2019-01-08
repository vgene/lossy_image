import socket
import sys
import struct
import traceback

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = ('10.0.2.2', 20008)

image = "./cute_dog.bmp"
fd = open(image, 'rb')
message = fd.read()
fd.close()
buffer_size = 4096
total_packet_number = (len(message) // buffer_size) + ((len(message) % buffer_size) > 0)

rand_identifier = 2123

for seq in range(0, total_packet_number):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        meta = struct.pack(">LLL", rand_identifier,  total_packet_number, seq)
        if (seq == total_packet_number - 1):
            sock.sendto(meta + message[seq * buffer_size:], server_address)
        else:
            sock.sendto(meta + message[seq * buffer_size: (seq+1) * buffer_size], server_address)

    except Exception as e:
        print("Something is wrong")
        traceback.print_exc()
    finally:
        sock.close()

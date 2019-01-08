import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('10.0.2.2', 20007)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
count = 0

image = "./cute_dog.bmp"
fd = open(image, 'rb')
message = fd.read()

try:
    # Send data
    #message = 'This is the message '+str(count)
    #msg = str.encode(message)
    print('sending {} bytes'.format(len(message)))
    sock.sendall(message)

except Exception as e:
    print("Something is wrong")
finally:
    fd.close()
    sock.close()

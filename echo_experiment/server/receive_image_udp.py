import socket
import sys
import time

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Bind the socket to the port
server_address = ('127.0.0.1', 20008)
print('starting UDP up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
# sock.listen(1)

buffer_size = 4096
while True:
    # Wait for a connection
    seq = 0
    image = b''

    try:
        print('connection from {}'.format(client_address))

        # Receive the data in small chunks and retransmit it
        while True:
            data, address = sock.recvfrom(buffer_size)
            #print('received {} bytes from {}'.format(len(data), client_address))
            image = image + data
            if not data:
                #print('no more data from {}'.format(client_address))
                print(len(image))
                break
    finally:
        # Clean up the connection
        # connection.close()
        end_time = time.time()
        print("--- {0:.4f} seconds ---".format(time.time() - start_time))

import socket
import sys
import time

# Settings
def write_to_file(data, filename="cute_dog_save.bmp"):
    f = open(filename, "wb")
    f.write(data)
    f.close()

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('127.0.0.1', 20007)
print('starting TCP up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

buffer_size = 4096
while True:
    # Wait for a connection
    print('\nwaiting for a connection')
    connection, client_address = sock.accept()
    start_time = time.time()
    try:
        print('connection from {}'.format(client_address))

        image = b''
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(buffer_size)
            #print('received {} bytes from {}'.format(len(data), client_address))
            image = image + data
            if not data:
                #print('no more data from {}'.format(client_address))
                print(len(image))
                write_to_file(image)
                break
    except Exception as e:
        print(e)
    finally:
        # Clean up the connection
        connection.close()
        end_time = time.time()
        print("--- {0:.4f} seconds ---".format(time.time() - start_time))

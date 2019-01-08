import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('127.0.0.1', 20007)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('\nwaiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('connection from {}'.format(client_address))

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            print('received {} bytes from {}'.format(len(data), client_address))
            if data:
                print('sending data back to the client')
                connection.sendall(data)
            else:
                print('no more data from {}'.format(client_address))
                break
    finally:
        # Clean up the connection
        connection.close()

import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('10.0.2.2', 20007)
print('connecting to {} port {}'.format(*server_address))
sock.connect(server_address)
count = 0

for i in range(0, 10):
    try:
        # Send data
        message = 'This is the message '+str(count)
        msg = str.encode(message)
        print('sending ' + message)
        sock.sendall(msg)

        # Look for the response
        amount_received = 0
        amount_expected = len(msg)
        
        while amount_received < amount_expected:
            data = sock.recv(16)
            amount_received += len(data)
            print('received {}'.format(data))
    except Exception as e:
        print("Something is wrong")

    finally:
        count = count + 1
        #print >>sys.stderr, 'closing socket'
        #sock.close()
sock.close()

import socket
import sys

# Create a UDP socket
server_address = ('10.0.2.2', 20008)
message = b'This is the message '
count = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
for i in range(0,10):
    try:
        sock.settimeout(1.0)
        msg = message + str.encode(str(count))
        # Send data
        print('sending {!r}'.format(msg))
        sent = sock.sendto(msg, server_address)

        # Receive response
        #print('waiting to receive')
        data, server = sock.recvfrom(4096)
        #print('received {!r}'.format(data))
    except Exception as e:
        print('Something is wrong')
        sock.close()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    finally:
        count = count + 1
        #print('closing socket')
        #sock.close()

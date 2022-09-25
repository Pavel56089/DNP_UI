from socket import socket, AF_INET, SOCK_STREAM
import sys

numbers = [
    15492781, 15492787, 15492803,
    15492811, 15492810, 15492833,
    15492859, 15502547, 15520301,
    15527509, 15522343, 1550784
    ]
# Host and port are passed as arguments
args = sys.argv[1].split(':')
HOST = args[0]
PORT = int(args[1])

# Try to connect to the server
with socket(AF_INET, SOCK_STREAM) as sock:
    sock.connect((HOST, int(PORT)))
    # Send the numbers to the server
    print('Connected to (' + str(HOST) + ',' + str(PORT) + ')')
    sock.sendall(str.encode('\n'.join([str(number) for number in numbers])))
    chunk = sock.recv(1024)
    data = chunk.decode().split('\n')
    print(*data, sep='\n')
    print('Completed')
    exit()
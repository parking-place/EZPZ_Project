from socket import *
import pandas as pd

WEB_HOST_NAME = 'EZPZ_WEB'
WEB_IP = gethostbyname(WEB_HOST_NAME)
PORT = 12345

server_socker = socket(AF_INET, SOCK_STREAM)
server_socker.bind((WEB_IP, PORT))
server_socker.listen(1)

connection_socket, addr = server_socker.accept()

print('Connection address:', str(addr))

data = connection_socket.recv(1024)

data_df = pd.read_json(data.decode('utf-8'))

print('Received data:', data_df)

connection_socket.send('Hello from ezpz_web'.encode('utf-8'))
print('Complete sending data')
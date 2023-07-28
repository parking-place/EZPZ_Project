from socket import *
import pandas as pd

data_dict = {
    'name': ['A', 'B', 'C', 'D', 'E'],
    'num': [1, 2, 3, 4, 5]
}

data_df = pd.DataFrame(data_dict)

WEB_HOST_NAME = 'EZPZ_WEB'
WEB_IP = gethostbyname(WEB_HOST_NAME)
PORT = 12345

client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((WEB_IP, PORT))

print('Connected to {}:{}'.format(WEB_IP, PORT))

client_socket.send(data_df.to_json().encode('utf-8'))

data = client_socket.recv(1024)
print('Received from server: {}'.format(data.decode('utf-8')))

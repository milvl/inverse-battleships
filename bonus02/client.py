"""
This is a simple testing script for the C server. It runs multiple clients that connect to the server and send/receive data.
Testing is done on localhost:8080.
"""

import random
import socket
import threading

HOST = '127.0.0.1'
PORT = 8080
BUFFER_SIZE = 1024

CORRECT_INTERACTION = 0
AUTHENTICATION_FAIL = 1
VALIDATION_FAIL = 2
VALIDATION_FAIL_STR = 3
DISCONNECT_BEFORE_AUTH = 4
DISCONNECT_BEFORE_VAL = 5

def client_thread(id, interaction):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as new_socket:
        new_socket.settimeout(2)
        try:
            # connect to the server
            new_socket.connect((HOST, PORT))
            print(f'Client {id}: Connected to server at {HOST}:{PORT} from port {new_socket.getsockname()[1]}')
            
            # send data to the server
            message = f'HELLO\n'
            if interaction == AUTHENTICATION_FAIL:
                message = f'BYE\n'
            
            if interaction == DISCONNECT_BEFORE_AUTH:
                raise Exception('Client disconnected before authentication')

            new_socket.sendall(message.encode('ascii'))
            print(f'Client {id}: Sent to server: {message.strip()}')
            
            # receive data from the server
            data = new_socket.recv(BUFFER_SIZE)
            print(f'Client {id}: Received from server: {data.decode("ascii").strip()}')

            # check if the connection is still alive
            if data == b'WRONG\n':
                data = new_socket.recv(1)
                if data == b'' or not data:
                    raise Exception('Connection closed by the server')

            # expected response = 'NUM:<number>\n'
            num = int(data.decode('ascii').split(':')[1].strip())
            print(f'Client {id}: Extracted number: {num}')

            # send the number back to the server
            message = f'{num*2}\n'
            if interaction == VALIDATION_FAIL:
                message = f'{num*2 + 1}\n'
            elif interaction == VALIDATION_FAIL_STR:
                message = f'some_error\n'

            new_socket.sendall(message.encode('ascii'))
            print(f'Client {id}: Sent to server: {message.strip()}')

            if interaction == DISCONNECT_BEFORE_VAL:
                raise Exception('Client disconnected before validation')

            # receive data from the server
            data = new_socket.recv(BUFFER_SIZE)
            print(f'Client {id}: Received from server: {data.decode("ascii").strip()}')

            data = new_socket.recv(1)
            if data == b'' or not data:
                raise Exception('Connection closed by the server')
        except Exception as e:
            print(f'Client {id}: {e}')

def main():
    num_clients = 6
    threads = []

    # create and start client threads
    for i in range(num_clients):
        thread = threading.Thread(target=client_thread, args=(i, i))
        thread.start()
        threads.append(thread)
    
    # wait for all threads to finish
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()

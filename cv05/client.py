import socket

HOST = '147.228.67.113'
PORT = 4242

# create a TCP/IP socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    s.sendall(b'Hello, server!')

    # Receive the server's response
    data = s.recv(1024)

# Print the server's response
print(f"Received {data!r}")

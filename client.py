import socket

IP, PORT = "127.0.0.1", 8080
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((IP, PORT))

sock.send("hello world".encode())
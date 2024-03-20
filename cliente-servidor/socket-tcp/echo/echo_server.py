# echo-server.py - https://realpython.com/python-sockets/#echo-client-and-server

import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    # with conn:
    print(f"Starting up echo server on {HOST}:{PORT}")
    while True:
        try:
            conn, addr = s.accept() 
            data = conn.recv(1024)
            if data:
                conn.sendall(data)
                print(f"Received {data.decode('utf-8')!r} from {addr}")
                conn.close()
        except KeyboardInterrupt:
            print("Closing server")
            s.close()
            break
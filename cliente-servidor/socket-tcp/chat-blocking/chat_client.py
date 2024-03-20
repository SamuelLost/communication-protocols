import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("Connected to server")
    s.connect((HOST, PORT))
    while True:
        try:
            # s.sendall(b"Hello, world")
            data_send = input(f"{'':>{80 // 2}}")
            if len(data_send) != 0:
                s.send(data_send.encode('utf-8'))
            data = s.recv(1024)
            if data:
                print(f"Márcia: {data.decode('utf-8')}")
        except KeyboardInterrupt:
            s.close()
            print("Closing client")
            break

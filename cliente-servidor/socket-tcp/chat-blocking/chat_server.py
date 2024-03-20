import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    
    conn, addr = s.accept()  
    print(f"Connected by {addr}")
    print("Connected to server")
    with conn:
        print(f"Starting up echo server on {HOST}:{PORT}")
        while True:
            try:
                data = conn.recv(1024)
                if data:
                    # print(data.decode('utf-8'))
                    print(f"Tadeu: {data.decode('utf-8')}")
                data_send = input(f"{'':>{80 // 2}}")
                if len(data_send) != 0:
                    conn.send(data_send.encode('utf-8'))
                # conn.sendall(data_send.encode('utf-8'))
            except KeyboardInterrupt:
                print("Closing server")
                conn.close()
                s.close()
                break
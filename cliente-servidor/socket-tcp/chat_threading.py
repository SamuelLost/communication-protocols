import socket
import threading

# Use with netcat(nc)
# Execute this file in one terminal, open a new terminal for netcat
# Execute: nc HOST PORT and starts type

# Bind to socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 11111))
s.listen(2)

def chat(conn, addr):
    while True:
        text = conn.recv(4096)
        if not text: break
        print(text.decode())


if __name__ == '__main__':
    ## Accept connections and start new thread
    conn, addr = s.accept()
    threading.Thread(target=chat, args=(conn, addr), daemon=True).start()

    # get user input and send message
    while True:
        msg = input(">>>")
        conn.sendall(msg.encode() + b'\n')

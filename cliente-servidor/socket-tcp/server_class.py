import socket

class SocketServer:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        else:
            self.sock = sock
    
    def connect(self, host, port):
        server_address = (host, port)
        self.sock.bind(server_address)
        self.sock.listen(5)

    def accept(self):
        return self.sock.accept()
    
    def send(self, data):
        self.sock.send(data)

    def recv(self, size):
        return self.sock.recv(size)
    
    def close(self):
        self.sock.close()

'''
# How to use it
import server_class

if __name__ == "__main__":
    sock = server.SocketServer()
    sock.connect('localhost', 9090)

    while True:
        try:
            client, addr = sock.accept()
            data = client.recv(2048).decode('utf-8')
            if data:
                print(data)
                client.send(data.encode('utf-8'))
                print ("sent %s bytes back to %s" % (data, addr))
                client.close()
        except KeyboardInterrupt:
            print("Closing server")
            sock.close()
            break
'''
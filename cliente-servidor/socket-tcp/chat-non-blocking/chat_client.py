#!/usr/bin/venv python

import socket
import select
import sys
import signal
import pickle
import struct

SERVER_HOST = 'localhost'

def send(channel, *args):
    buffer = pickle.dumps(args) # Serialize the object
    value = socket.htonl(len(buffer)) # Convert 32-bit positive integers from host to network byte order
    size = struct.pack("L",value) # Pack the 4-byte integer into a byte string. "L" is for unsigned long
    channel.send(size) # Send the size of the message. This allows the receiver to know how many bytes to expect in the upcoming message.
    channel.send(buffer) # Send the message

def receive(channel):
    size = struct.calcsize("L") # Calculate the size of the message
    size = channel.recv(size) # Receive the size of the message
    try:
        size = socket.ntohl(struct.unpack("L",size)[0]) # Convert 32-bit positive integers from network to host byte order
    except struct.error as e:
        return ''
    
    buf = ""
    while len(buf) < size:
        buf = channel.recv(size - len(buf))
    return pickle.loads(buf)[0] # Deserialize the object


class ChatClient:
    """ A command line chat client using select """
    def __init__(self, name, port, host=SERVER_HOST):
        self.name = name
        self.connected = False
        self.host = host
        self.port = port

        # Initial prompt
        self.prompt = f"[{name}@{socket.gethostname().split('.')[0]}]"

        # Connect to the server
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, self.port))
            print(f"Connected to the chat server@{self.port}")
            self.connected = True

            # Send my name...
            send(self.sock, f"NAME: {self.name}")
            data = receive(self.sock)

            # Contais client address, set it
            addr = data.split('CLIENT: ')[1]
            self.prompt = f"[{self.name}@{addr}]" # Change the prompt 
        except socket.error as e:
            print(f"Failed to connect to chat server@{self.port}")
            sys.exit(1)

    def run(self):
        """ Chat client main loop """
        while self.connected:
            try:
                sys.stdout.write(f"{self.prompt} > ")
                sys.stdout.flush()
                # Wait for input from stdin and socket
                readable, writeable, exceptional = select.select([0, self.sock], [], [])
                for sock in readable:
                    if sock == 0:
                        data = sys.stdin.readline().strip() # Read from stdin
                        if data: send(self.sock, data) # Send the data
                    elif sock == self.sock:
                        data = receive(self.sock)
                        if not data:
                            print("Client shutting down.")
                            self.connected = False
                            break
                        else:
                            sys.stdout.write(data + '\n')
                            sys.stdout.flush()
            except KeyboardInterrupt:
                print("Client interrupted.")
                self.sock.close()
                break
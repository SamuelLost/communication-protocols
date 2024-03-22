#!/usr/bin/env python

import socket
import select
import sys
import signal
import pickle
import struct

CHAT_SERVER_NAME = 'server'

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

class ChatServer:
    """ Chat server using select """
    # Select is a monitoring function that watches for I/O events on the list of sockets
    def __init__(self, port, backlog=5):
        self.clients = 0
        self.clientmap = {}
        self.outputs = [] # list output sockets

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Create a new socket
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Enable reusing the same address
        self.server.bind(("", port))

        #print (f'Server listening to port: {port}...')
        print(f"Server listening to {self.server.getsockname()}")
        self.server.listen(backlog)

        # Register signal handler
        signal.signal(signal.SIGINT, self.signal_handler) # Register a signal handler for SIGINT (Ctrl+C)
        signal.signal(signal.SIGTERM, self.signal_handler) # Register a signal handler for SIGTERM

    def signal_handler(self, signum, frame):
        """ Clean up client outputs """
        if signum == signal.SIGINT:
            print('Caught signal SIGINT')
        elif signum == signal.SIGTERM:
            print('Caught signal SIGTERM')
        
        print ('Shutting down server...')
        # Remove the server socket from the list of readable and writable sockets
        for output in self.outputs: # Close all the client sockets
            output.close()

        self.server.close()

    def get_client_name(self, client):
        """ Return the name of the client """
        info = self.clientmap[client]
        host, name = info[0][0], info[1]
        return '@'.join((name, host))
    
    def run(self):
        inputs = [self.server, sys.stdin] # File descriptors to be monitored for read events
        self.outputs = []
        running = True
        while running:
            try:
                # Watch for events on the sockets
                readable, writeable, exceptional = \
                    select.select(inputs, self.outputs, []) # ARGS=(Potencial read, write, and error events)
            except select.error as e:
                break
            
            for sock in readable:
                if sock == self.server:
                    client, address = self.server.accept()
                    print(f"Chat server: got connection {client.fileno()} from {address}")
                    # Read the login name
                    cname = receive(client).split('NAME: ')[1]
                    self.clients += 1
                    send(client, 'CLIENT: ' + str(address[0]))
                    inputs.append(client)
                    self.clientmap[client] = (address, cname)
                    # Send joining information to other clients
                    msg = f"\n(Connected: New client ({self.clients}) from {self.get_client_name(client)})"
                    
                    for output in self.outputs:
                        send(output, msg) # Send the message to all the clients
                    self.outputs.append(client)
                elif sock == sys.stdin:
                    # handle standard input
                    junk = sys.stdin.readline()
                    running = False
                else:
                    # handle all other sockets
                    try:
                        data = receive(sock)
                        if data:
                            # Send as new client's message...
                            msg = f"\n#[{self.get_client_name(sock)}]>> {data}"
                            # Send data to all except ourself
                            for output in self.outputs:
                                if output != sock:
                                    send(output, msg)
                        else:
                            print (f"Chat server: {sock.fileno()} hung up")
                            self.clients -= 1
                            sock.close()
                            inputs.remove(sock)
                            self.outputs.remove(sock)
                            # Sending client leaving information to others
                            msg = f"\n(Now hung up: Client from {self.get_client_name(sock)})"
                            for output in self.outputs:
                                send(output, msg)
                    except socket.error as e:
                        # Remove
                        inputs.remove(sock)
                        self.outputs.remove(sock)
                        print (f"Chat server: {sock.fileno()} hung up unexpectly")
        self.server.close()

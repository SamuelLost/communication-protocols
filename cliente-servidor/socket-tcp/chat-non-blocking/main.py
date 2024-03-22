#!/usr/bin/env python

import argparse
import chat_client
import chat_server

def main():
    parser = argparse.ArgumentParser(description="Socket Server/Client")
    parser.add_argument('-t', '--type', choices=['server', 'client'], required=True, 
                        type=str, help='Type of the connection')
    parser.add_argument('-n','--name', required=True, type=str, help='Username')
    parser.add_argument('-p','--port', required=True, type=int, help='Port')
    parser.add_argument('-s','--server', required=False, type=str, help='Server IP', default='localhost')
    args = parser.parse_args()

    if args.type == 'server':
        server = chat_server.ChatServer(args.port)
        server.run()
    else:
        client = chat_client.ChatClient(args.name, args.port, args.server)
        client.run()

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter02/udp_remote.py
# UDP client and server for talking over the network
import argparse, random, socket, sys
from tkinter import *
from tkinter import filedialog
MAX_BYTES = 65535


def split_file(path_file, chunk_size):
    files = []
    with open(path_file, "rb") as fi:
            buf = fi.read(chunk_size)
            while (buf):
               files.append(buf)
               buf = fi.read(chunk_size)
    return files


def server(interface, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((interface, port))
    print('Listening at', sock.getsockname())
    while True:
        data, address = sock.recvfrom(MAX_BYTES)
        if random.random() < 0.5:
            print('Pretending to drop packet from {}'.format(address))
            continue
        text = data.decode('ascii')
        print('The client at {} says {!r}'.format(address, text))
        message = 'Your data was {} bytes long'.format(len(data))
        sock.sendto(message.encode('ascii'), address)


def client(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = sys.argv[2]
    sock.connect((hostname, port))
    print('Client socket name is {}'.format(sock.getsockname()))
    delay = 0.1 # seconds
    # Select the file
    root = Tk()
    root.filename =  filedialog.askopenfilename(initialdir = ".",title = "Selecciona Archivo",filetypes = (("jpeg files","*.jpg"),("all files","*.*")))
    files = split_file(root.filename, 4096)
    print(f"File splited in {len(files)}")
    for i, file in enumerate(files):
        datagram = {
            "id": 1500
            "N": i,
            "data": file
        }
        datagram = json.dumps(datagram).encode('utf-8')
        sock.send(datagram)
        print('Waiting up to {} seconds for a reply'.format(delay))
        sock.settimeout(delay)
        # Recive the ACK
        try:
            data = sock.recv(MAX_BYTES)
        except socket.timeout:
            delay *= 2 # wait even longer for the next request
            if delay > 2.0:
                raise RuntimeError('I think the server is down')
        while data.decode('ascii') != 'A':
            
    print('The server says {!r}'.format(data.decode('ascii')))

if __name__ == '__main__':
    choices = {'client': client, 'server': server}
    parser = argparse.ArgumentParser(description='Send and receive UDP,'
    ' pretending packets are often dropped')
    parser.add_argument('role', choices=choices, help='which role to take')
    parser.add_argument('host', help='interface the server listens at;'
    'host the client sends to')
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
    help='UDP port (default 1060)')
    args = parser.parse_args()
    function = choices[args.role]
    function(args.host, args.p)
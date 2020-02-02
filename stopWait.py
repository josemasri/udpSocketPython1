#!/usr/bin/env python3
# Foundations of Python Network Programming, Third Edition
# https://github.com/brandon-rhodes/fopnp/blob/m/py3/chapter02/udp_remote.py
# UDP client and server for talking over the network
import argparse, random, socket, sys
import os.path
import json
import base64


MAX_BYTES = 65535

def split_file(path_file, chunk_size):
    files = []
    with open(path_file, "rb") as fi:
            buf = fi.read(chunk_size)
            while (buf):
               files.append(buf)
               buf = fi.read(chunk_size)
    return files

def create_file(fileName, dataArr):
    f = open("img.jpg", "w+b")
    for file in dataArr:
        f.write(file)
    f.close()




def server(interface, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((interface, port))
    print('Listening at', sock.getsockname())
    while True:
        sock.settimeout(None)
        data, address = sock.recvfrom(MAX_BYTES)
        file_name = data.decode('ascii')
        print('The client at {} request file {!r}'.format(address, file_name))
        if os.path.isfile(file_name):
            # Code if file exist
            files = split_file(file_name, MAX_BYTES - 20000)
            res = {
                "ok": True,
                "nDatagrams": len(files)
            }
            datagram = json.dumps(res).encode('utf-8')
            sock.sendto(datagram, address)

            delay = 0.1
            i = 0
            while i < len(files):
                try:
                    data2, address2 = sock.recvfrom(MAX_BYTES)
                except socket.timeout:
                    delay *= 2 # wait even longer for the next request
                    if delay > 2.0:
                        i -= 1
                        res = {
                            "id": i,
                            "data": base64.encodebytes(files[i]).decode("utf-8")
                        }
                        datagram = json.dumps(res).encode('utf-8')
                        sock.sendto(datagram, address)
                        delay = 0.1
                        sock.settimeout(delay)
                else:
                    delay = 0.1
                    data2Dec = json.loads(data2.decode('utf-8'))
                    if address == address2 and data2Dec['id'] == i:
                        res = {
                            "id": i,
                            "data": base64.encodebytes(files[i]).decode("utf-8")
                        }
                        datagram = json.dumps(res).encode('utf-8')
                        sock.sendto(datagram, address)
                        sock.settimeout(delay)
                        i += 1
                    else:
                        print("An error ocurred")
                        break
            # sock.settimeout(0)
        else:
            # Code if file don't exist
            res = {
                "ok": False,
                "message": "The file don't exist"
            }
            datagram = json.dumps(res).encode('utf-8')
            sock.sendto(datagram, address)

def client(hostname, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    hostname = sys.argv[2]
    sock.connect((hostname, port))
    print('Client socket name is {}'.format(sock.getsockname()))
    delay = 0.1 # seconds
    # Client requesting the file
    print("Enter the file name to download: ")
    file_name = input()
    data = file_name.encode('ascii')
    while True:
        sock.send(data)
        print('Waiting up to {} seconds for a reply'.format(delay))
        sock.settimeout(delay)
        try:
            data = sock.recv(MAX_BYTES)
        except socket.timeout:
            delay *= 2 # wait even longer for the next request
            if delay > 2.0:
                raise RuntimeError('I think the server is down')
        else:
            res = json.loads(data.decode('utf-8'))
            if res['ok']:
                print("File exists, i will recive {} datagrams".format(res['nDatagrams']))
                nDatagrams = res['nDatagrams']
                files = []
                delay = 0.1 # seconds
                i = 0
                while i < nDatagrams:
                    res = {
                            "ok": True,
                            "id": i
                    }
                    datagramRes = json.dumps(res).encode('utf-8')
                    sock.send(datagramRes)
                    sock.settimeout(delay)
                    try:
                        data2 = sock.recv(MAX_BYTES)
                    except socket.timeout:  
                        delay *= 2 # wait even longer for the next request
                        if delay > 2.0:
                            i -= 1
                            res = {
                                "ok": True,
                                "id": i
                            }
                            datagramRes = json.dumps(res).encode('utf-8')
                            sock.send(datagramRes)
                            delay = 0.1
                            sock.settimeout(delay)
                    else:
                        delay = 0.1 # seconds
                        datagram2 = json.loads(data2.decode('utf-8'))
                        files.append( base64.decodebytes(datagram2['data'].encode("utf-8")) )
                        i += 1
                create_file(file_name, files)
                print("File {} downloaded succesfuly".format(file_name))
            else:
                print(res['message'])
            break # we are done, and can stop looping
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
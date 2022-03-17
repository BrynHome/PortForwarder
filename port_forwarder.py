import socket
import threading
import sys

BACKLOG = 10
BUFF_SIZE = 4096

def main() :
    configurations = config()
    for settings in configurations:
        a = threading.Thread(target=thread, args=settings)
        a.start()


def config():
    configurations = list()
    file = open("port_forward.config", "r")
    lines = file.readlines()
    for line in lines :
        splits = line.split()
        configurations.append((int(splits[0]), splits[1], int(splits[2])))
    return configurations


def create_sock(addr):
    if socket.has_dualstack_ipv6():
        return socket.create_server(addr, family=socket.AF_INET6, dualstack_ipv6=True)
    else:
        return socket.create_server(addr)


def thread(*settings):
    # server_sock = create_sock(('', settings[0]))
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(('', settings[0]))
    server_sock.listen(BACKLOG)
    # ADD LOGGING HERE
    while True:
        src_sock, src_address = server_sock.accept()
        #ADD LOGGING
        try:
            out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            out_sock.connect((settings[1], settings[2]))
            #ADD LOGGING
            src_to_dest = threading.Thread(target=traffic, args=(src_sock, out_sock))
            dest_to_src = threading.Thread(target=traffic, args=(out_sock, src_sock))
            src_to_dest.start()
            dest_to_src.start()
        except Exception as e:
            print("Temp err")
            # ADD LOGGING


def traffic(src, dest) :
    src_host, src_port = src.getsockname()
    dest_host, dest_port = dest.getsockname()
    while True:
        try:
            buf = src.recv(BUFF_SIZE)
            #ADD LOGGING?
            dest.send(buf)
        except Exception as e:
            print("Err temp")
            break
    print("Close src & dest temp")
    src.close()
    dest.close()


if __name__ == '__main__':
    main()

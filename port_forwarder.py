import signal
import socket
import threading
import sys
import time

BACKLOG = 10
BUFF_SIZE = 4096


def main():
    configurations = config()
    a = []
    try:
        for settings in configurations:
            a.append(threading.Thread(target=thread, args=settings, daemon=True))
            a[len(a) - 1].start()
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print("Exiting server")
        exit(1)


def config():
    configurations = list()

    try:
        file = open("port_forward.config", "r")
        lines = file.readlines()
        if len(lines) == 0:
            print("Config file empty")
            exit(0)

        for line in lines:
            splits = line.split()
            configurations.append((int(splits[0]), splits[1], int(splits[2])))
        return configurations
    except FileNotFoundError as e:
        print("Configuration not found")
        exit(0)


def create_sock(addr):
    if socket.has_dualstack_ipv6():
        return socket.create_server(addr, family=socket.AF_INET6, reuse_port=True, dualstack_ipv6=True)
    else:
        return socket.create_server(addr, family=socket.AF_INET, reuse_port=True)


def thread(*settings):
    server_sock = 0
    # server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # server_sock.bind(('', settings[0]))
    try:
        server_sock = create_sock(('', settings[0]))
        server_sock.listen(BACKLOG)
    except Exception as e:
        print("Error starting listening on port " + str(settings[0]) + ". Traffic for this port will not be forwarded.")
        return

    print(
        "Server Listening on port " + str(settings[0]) + " forwarding to " + settings[1] + " port " + str(settings[2]))
    # ADD LOGGING HERE
    while True:
        src_sock, src_address = server_sock.accept()
        if type(src_address) is tuple:
            print("PORT " + str(settings[0]) + ":Inbound connection from" + src_address[0] + ". Forwarding to "
                  + settings[1] + " port " + str(settings[2]))
        else:
            print("PORT " + str(settings[0]) + ":Inbound connection from" + src_address + ". Forwarding to "
                  + settings[1] + " port " + str(settings[2]))
        # ADD LOGGING
        try:
            out_sock = socket.create_connection((settings[1], settings[2]))
            # out_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # out_sock.connect((settings[1], settings[2]))
            # ADD LOGGING
            print("Connection established with " + settings[1] + " port " + str(settings[2]))
            src_to_dest = threading.Thread(target=traffic, args=(src_sock, out_sock))
            dest_to_src = threading.Thread(target=traffic, args=(out_sock, src_sock))
            src_to_dest.start()
            dest_to_src.start()
        except Exception as e:
            print("Error during connection")
            # ADD LOGGING


def traffic(src, dest):
    src_info = src.getsockname()
    dest_info = dest.getsockname()
    buf = ' '
    while buf:
        try:
            buf = src.recv(BUFF_SIZE)
            if buf:
                print("Forwarding from " + src_info[0] + " port " + str(src_info[1]) + " to "
                      + dest_info[0] + " port " + str(src_info[1]))
                dest.send(buf)
            else:
                print("Closing " + src_info[0])
                dest.send(buf)
                dest.shutdown()
                #dest.close()
                break
            # ADD LOGGING?
        except Exception as e:
            print("Closing conn " + dest_info[0])
            src.close()
            dest.close()
            break


if __name__ == '__main__':
    main()

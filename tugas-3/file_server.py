from socket import *
import socket
import threading
import logging
import time
import sys

from file_protocol import FileProtocol
fp = FileProtocol()

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        buffer = ''
        while True:
            try:
                data = self.connection.recv(1024)
                if not data:
                    break
                buffer += data.decode()

                # tunggu sampai end marker '\r\n\r\n' diterima
                if '\r\n\r\n' in buffer:
                    full_message, buffer = buffer.split('\r\n\r\n', 1)
                    logging.warning(f"received full message from {self.address}")
                    hasil = fp.proses_string(full_message)
                    hasil = hasil + '\r\n\r\n'
                    self.connection.sendall(hasil.encode())
            except Exception as e:
                logging.error(f"Error while processing client {self.address}: {e}")
                break
        self.connection.close()


class Server(threading.Thread):
    def __init__(self, ipaddress='0.0.0.0', port=8889):
        self.ipinfo = (ipaddress, port)
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        threading.Thread.__init__(self)

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(5)
        while True:
            self.connection, self.client_address = self.my_socket.accept()
            logging.warning(f"connection from {self.client_address}")
            clt = ProcessTheClient(self.connection, self.client_address)
            clt.start()
            self.the_clients.append(clt)


def main():
    svr = Server(ipaddress='0.0.0.0', port=1231)
    svr.start()


if __name__ == "__main__":
    main()

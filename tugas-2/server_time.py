from socket import *
import socket
import threading
import logging
from datetime import datetime

class ProcessTheClient(threading.Thread):
    def __init__(self, connection, address):
        self.connection = connection
        self.address = address
        threading.Thread.__init__(self)

    def run(self):
        try:
            while True:
                data = b''
                while not data.endswith(b'\r\n'):
                    chunk = self.connection.recv(32)
                    if not chunk:
                        logging.warning(f"Connection closed by {self.address}")
                        return
                    data += chunk

                decoded_data = data.decode('utf-8').strip()
                logging.info(f"Received from {self.address}: {decoded_data}")

                if decoded_data.upper() == 'TIME':
                    current_time = datetime.now().strftime('%H:%M:%S')
                    response = f'JAM {current_time}\r\n'
                    self.connection.sendall(response.encode('utf-8'))
                elif decoded_data.upper() == 'QUIT':
                    logging.info(f"Client {self.address} requested to quit.")
                    break
                else:
                    response = 'INVALID REQUEST\r\n'
                    self.connection.sendall(response.encode('utf-8'))
        except Exception as e:
            logging.error(f"Error handling client {self.address}: {e}")
        finally:
            self.connection.close()
            logging.info(f"Connection with {self.address} closed.")

class Server(threading.Thread):
    def __init__(self, port=45000):
        self.the_clients = []
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = port
        threading.Thread.__init__(self)

    def run(self):
        self.my_socket.bind(('0.0.0.0', self.port))
        self.my_socket.listen(5)
        logging.info(f"Time Server running on port {self.port}...")

        while True:
            connection, client_address = self.my_socket.accept()
            logging.info(f"Connection from {client_address}")
            clt = ProcessTheClient(connection, client_address)
            clt.start()
            self.the_clients.append(clt)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    svr = Server()
    svr.start()

if __name__ == "__main__":
    main()
import socket
import logging
from concurrent.futures import ThreadPoolExecutor
from file_protocol import FileProtocol

HOST = '0.0.0.0'
PORT = 1231
BUFFER_SIZE = 1024

def handle_client(conn, addr):
    logging.warning(f"Connection from {addr} established")
    data_received = ''
    while True:
        data = conn.recv(BUFFER_SIZE)
        if not data:
            break
        data_received += data.decode()
        if "\r\n\r\n" in data_received:
            break

    fp = FileProtocol()
    response = fp.proses_string(data_received.strip())
    response += "\r\n\r\n"
    conn.sendall(response.encode())
    conn.close()
    logging.warning(f"Connection from {addr} closed")

def main():
    logging.basicConfig(level=logging.WARNING)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(100)
    logging.warning(f"Server running on {HOST}:{PORT}")

    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            conn, addr = server_socket.accept()
            executor.submit(handle_client, conn, addr)

if __name__ == '__main__':
    main()

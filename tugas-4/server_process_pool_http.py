import socket
import time
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
from http_implementation import HttpServer

# Konfigurasi logging agar output lebih terlihat
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

httpserver = HttpServer()

def ProcessTheClient(connection, address):
    """
    Fungsi ini akan dijalankan sebagai sebuah proses terpisah
    untuk menangani setiap koneksi klien.
    """
    rcv = ""
    # Logging di dalam process:
    logging.warning(f"Process {multiprocessing.current_process().name} handling connection from {address}")
    try:
        while True:
            data = connection.recv(32)
            if data:
                d = data.decode()
                rcv = rcv + d
                if rcv.endswith('\r\n\r\n'): # Mengubah deteksi akhir request untuk POST
                    logging.warning(f"Data dari client {address}: {rcv.strip()}")
                    hasil = httpserver.proses(rcv)
                    hasil = hasil + "\r\n\r\n".encode()
                    logging.warning(f"Balas ke client {address}: {hasil[:100]}...") # Log sebagian hasil saja
                    connection.sendall(hasil)
                    break # Keluar dari loop setelah request diproses
            else:
                break # Klien menutup koneksi
    except OSError as e:
        logging.error(f"OSError in ProcessTheClient for {address}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error in ProcessTheClient for {address}: {e}")
    finally:
        connection.close()
        logging.warning(f"Connection from {address} closed by process {multiprocessing.current_process().name}")
    return


def Server():
    the_clients = []
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    my_socket.bind(('0.0.0.0', 8885))
    my_socket.listen(1)
    logging.warning("Server started on port 8885")

    # Menggunakan ProcessPoolExecutor
    # Jumlah proses biasanya disesuaikan dengan jumlah core CPU Anda
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor: # Perubahan di sini
        while True:
            connection, client_address = my_socket.accept()
            logging.warning(f"Connection from {client_address}")
            
            # Submit tugas ke process pool
            # executor.submit akan membuat proses baru atau menggunakan yang sudah ada dari pool
            p = executor.submit(ProcessTheClient, connection, client_address)
            the_clients.append(p)
            
            # Membersihkan daftar future yang sudah selesai untuk menghindari kebocoran memori
            the_clients = [c for c in the_clients if not c.done()]
            
            # Menampilkan jumlah proses yang aktif atau sedang menunggu hasil
            logging.warning(f"Jumlah tasks aktif/pending di pool: {len(the_clients)}")


def main():
    Server()

if __name__=="__main__":
    main()
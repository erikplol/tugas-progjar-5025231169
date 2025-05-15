import socket
import json
import base64
import logging
import shlex

server_address = ('0.0.0.0', 7777)


def send_command(command_str=""):
    global server_address
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(server_address)
    logging.warning(f"connecting to {server_address}")
    try:
        command_str += "\r\n\r\n"
        logging.warning(f"sending message ")
        sock.sendall((command_str).encode())
        data_received = ""  # empty string
        while True:
            data = sock.recv(16)
            if data:
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                break
        hasil = json.loads(data_received)
        logging.warning("data received from server:")
        return hasil
    except Exception as e:
        logging.warning(f"error during data receiving: {e}")
        return False


def remote_list():
    command_str = f"LIST\r\n"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print("daftar file : ")
        for nmfile in hasil['data']:
            print(f"- {nmfile}")
        return True
    else:
        print("Gagal mendapatkan daftar file")
        return False


def remote_get(filename=""):
    command_str = f"GET {filename}\r\n"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        namafile = hasil['data_namafile']
        isifile = base64.b64decode(hasil['data_file'])
        with open(namafile, 'wb+') as fp:
            fp.write(isifile)
        print(f"File '{namafile}' berhasil di-download.")
        return True
    else:
        print("Gagal mendapatkan file")
        return False


def remote_upload(local_filename="", remote_filename=""):
    try:
        with open(local_filename, "rb") as f:
            file_content = f.read()
        encoded_content = base64.b64encode(file_content).decode('utf-8').strip()

        encoded_quoted = shlex.quote(encoded_content)

        command_str = f"UPLOAD {remote_filename} {encoded_quoted}\r\n"
        hasil = send_command(command_str)
        if hasil and hasil['status'] == 'OK':
            print(f"File '{local_filename}' berhasil di-upload sebagai '{remote_filename}'.")
            return True
        else:
            print("Gagal upload file:", hasil.get('data', 'Unknown error'))
            return False
    except FileNotFoundError:
        print(f"File '{local_filename}' tidak ditemukan.")
        return False

def remote_delete(remote_filename=""):
    command_str = f"DELETE {remote_filename}\r\n"
    hasil = send_command(command_str)
    if hasil and hasil['status'] == 'OK':
        print(f"File '{remote_filename}' berhasil dihapus dari server.")
        return True
    else:
        print("Gagal menghapus file:", hasil.get('data', 'Unknown error'))
        return False


if __name__ == '__main__':
    server_address = ('172.16.16.101', 1231)

    remote_list()
    remote_get('donalbebek.jpg')
    remote_upload('files/test_upload.jpg', 'files/test_upload.jpg')
    remote_list()
    remote_get('test_upload.jpg')
    remote_delete('test_upload.jpg')

import requests
import os
import logging

class HttpClient:
    def __init__(self, base_url="http://localhost:8885"):
        self.base_url = base_url

    def get_file_list(self):
        """Mengambil dan menampilkan daftar file dari server."""
        print(f"\nMengambil daftar file dari {self.base_url}/")
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            print("Daftar File:")
            print(response.text)
        except requests.exceptions.RequestException as e:
            print(f"Error saat mengambil daftar file: {e}")

    def upload_file(self, file_path):
        """Mengunggah file ke server."""
        if not os.path.exists(file_path):
            print(f"Error: File '{file_path}' tidak ditemukan.")
            return

        file_name = os.path.basename(file_path)
        print(f"\nMengunggah file '{file_name}' ke {self.base_url}/upload")
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f)}
                response = requests.post(f"{self.base_url}/upload", files=files)
                response.raise_for_status()
                print(f"Status Upload: {response.status_code} {response.reason}")
                print(f"Respon Server: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error saat mengunggah file: {e}")

    def delete_file(self, file_name):
        """Menghapus file dari server."""
        print(f"\nMenghapus file '{file_name}' dari {self.base_url}/{file_name}")
        try:
            response = requests.delete(f"{self.base_url}/{file_name}")
            response.raise_for_status()
            print(f"Status Hapus: {response.status_code} {response.reason}")
            print(f"Respon Server: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error saat menghapus file: {e}")

if __name__ == "__main__":
    client = HttpClient()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Client HTTP dimulai.")

    # --- Contoh Penggunaan ---

    # 1. Melihat daftar file
    logging.info("List file yang ada di server:")
    client.get_file_list()

    # 2. Mengunggah file
    logging.info("Mengunggah file contoh...")
    dummy_file_name = "contoh_upload.txt"
    with open(dummy_file_name, "w") as f:
        f.write("Ini adalah file yang diunggah sebagai contoh.")
    client.upload_file(dummy_file_name)
    logging.info("File contoh telah diunggah.")
    
    logging.info("Daftar file setelah upload:")
    client.get_file_list()

    # 3. Menghapus file
    logging.info("Menghapus file contoh...")
    client.delete_file(dummy_file_name)
    logging.info("File contoh telah dihapus.")
    
    logging.info("Daftar file setelah penghapusan:")
    client.get_file_list()

    # Menghapus file dummy lokal
    if os.path.exists(dummy_file_name):
        os.remove(dummy_file_name)
        print(f"\nFile lokal '{dummy_file_name}' telah dihapus.")
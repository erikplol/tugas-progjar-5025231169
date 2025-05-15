import json
import logging
import shlex

from file_interface import FileInterface
import base64

"""
* class FileProtocol bertugas untuk memproses 
data yang masuk, dan menerjemahkannya apakah sesuai dengan
protokol/aturan yang dibuat

* data yang masuk dari client adalah dalam bentuk bytes yang 
pada akhirnya akan diproses dalam bentuk string

* class FileProtocol akan memproses data yang masuk dalam bentuk
string
"""



class FileProtocol:
    def __init__(self):
        self.file = FileInterface()
    def proses_string(self, string_datamasuk=''):
        if string_datamasuk.upper().startswith("UPLOAD "):
            try:
                lines = string_datamasuk.split('\r\n')
                header = lines[0]
                base64_data = '\r\n'.join(lines[1:]).strip()

                filename = header.split(' ', 1)[1].strip()
                file_bytes = base64.b64decode(base64_data)

                with open(f'files/{filename}', 'wb') as f:
                    f.write(file_bytes)

                return json.dumps(dict(status='OK', data=f'File {filename} berhasil diupload'))
            except Exception as e:
                return json.dumps(dict(status='ERROR', data=f'Gagal upload file: {str(e)}'))

        # proses lainnya tetap seperti biasa (LIST, GET, DELETE)
        try:
            c = shlex.split(string_datamasuk)
            c_request = c[0].strip().upper()
            params = [x for x in c[1:]]
            if hasattr(self.file, c_request.lower()):
                cl = getattr(self.file, c_request.lower())(params)
                return json.dumps(cl)
            else:
                return json.dumps(dict(status='ERROR', data='request tidak dikenali'))
        except Exception as e:
            return json.dumps(dict(status='ERROR', data=f'Exception: {str(e)}'))


if __name__=='__main__':
    #contoh pemakaian
    fp = FileProtocol()
    print(fp.proses_string("LIST"))
    print(fp.proses_string("GET pokijan.jpg"))

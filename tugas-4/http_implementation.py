import sys
import os.path
import uuid
from glob import glob
from datetime import datetime
import os

class HttpServer:
    def __init__(self):
        self.sessions={}
        self.types={}
        self.types['.pdf']='application/pdf'
        self.types['.jpg']='image/jpeg'
        self.types['.txt']='text/plain'
        self.types['.html']='text/html'
    def response(self,kode=404,message='Not Found',messagebody=bytes(),headers={}):
        tanggal = datetime.now().strftime('%c')
        resp=[]
        resp.append("HTTP/1.0 {} {}\r\n" . format(kode,message))
        resp.append("Date: {}\r\n" . format(tanggal))
        resp.append("Connection: close\r\n")
        resp.append("Server: myserver/1.0\r\n")
        resp.append("Content-Length: {}\r\n" . format(len(messagebody)))
        for kk in headers:
            resp.append("{}:{}\r\n" . format(kk,headers[kk]))
        resp.append("\r\n")

        response_headers=''
        for i in resp:
            response_headers="{}{}" . format(response_headers,i)
        #menggabungkan resp menjadi satu string dan menggabungkan dengan messagebody yang berupa bytes
        #response harus berupa bytes
        #message body harus diubah dulu menjadi bytes
        if isinstance(messagebody, str):
            messagebody = messagebody.encode()

        response = response_headers.encode() + messagebody
        #response adalah bytes
        return response

    def proses(self,data):
        
        requests = data.split("\r\n")
        #print(requests)

        baris = requests[0]
        #print(baris)

        all_headers = [n for n in requests[1:] if n!='']

        j = baris.split(" ")
        try:
            method=j[0].upper().strip()
            if (method=='GET'):
                object_address = j[1].strip()
                return self.http_get(object_address, all_headers)
            if (method=='POST'):
                object_address = j[1].strip()
                return self.http_post(object_address, all_headers, requests) # Pass all requests for POST
            if (method=='DELETE'):
                object_address = j[1].strip()
                return self.http_delete(object_address, all_headers)
            else:
                return self.response(400,'Bad Request',b'',{})
        except IndexError:
            return self.response(400,'Bad Request',b'',{})
    def http_get(self,object_address,headers):
        files = glob('./*')
        #print(files)
        thedir='./'
        if (object_address == '/'):
            file_list_html = "<html><body><h1>List of Files:</h1><ul>"
            for file in files:
                file_list_html += f"<li><a href='/{os.path.basename(file)}'>{os.path.basename(file)}</a></li>"
            file_list_html += "</ul></body></html>"
            return self.response(200,'OK',file_list_html.encode(),dict())

        if (object_address == '/video'):
            return self.response(302,'Found',b'',dict(location='https://youtu.be/katoxpnTf04'))
        if (object_address == '/santai'):
            return self.response(200,'OK','santai saja'.encode(),dict())


        object_address=object_address[1:]
        if thedir+object_address not in files:
            return self.response(404,'Not Found',b'',{})
        fp = open(thedir+object_address,'rb') #rb => artinya adalah read dalam bentuk binary
        #harus membaca dalam bentuk byte dan BINARY
        isi = fp.read()
        
        fext = os.path.splitext(thedir+object_address)[1]
        content_type = self.types[fext]
        
        headers={}
        headers['Content-type']=content_type
        
        return self.response(200,'OK',isi,headers)
    
    def http_post(self, object_address, headers, requests):
        if object_address == '/upload':
            try:
                content_length = int([h.split(':')[1].strip() for h in headers if h.lower().startswith('content-length:')][0])
                # Extract the body of the POST request
                body_start = requests.index('') + 1  # Find the line after the empty line
                body = '\r\n'.join(requests[body_start:])
                
                # Extract filename and file content (crude, assumes simple form-data)
                filename_line = [line for line in requests if 'filename=' in line][0]
                filename = filename_line.split('filename="')[1].split('"')[0]
                
                content_start_marker = b'\r\n\r\n'  # Find the start of the content
                content_start_index = body.encode().find(content_start_marker) + len(content_start_marker)
                content_end_marker = b'\r\n------' # Find the end of the content
                content_end_index = body.encode().find(content_end_marker)
                
                file_content = body.encode()[content_start_index:content_end_index]

                with open(filename, 'wb') as f:  # Write in binary mode
                    f.write(file_content)
                return self.response(200, 'OK', f'File "{filename}" uploaded successfully.'.encode(), {})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'File upload failed: {str(e)}'.encode(), {})
        else:
             return self.response(404, 'Not Found', b'', {})

    def http_delete(self, object_address, headers):
        filepath = './' + object_address[1:]  # Remove the leading '/'
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return self.response(200, 'OK', f'File "{object_address[1:]}" deleted successfully.'.encode(), {})
            except Exception as e:
                return self.response(500, 'Internal Server Error', f'File deletion failed: {str(e)}'.encode(), {})
        else:
            return self.response(404, 'Not Found', f'File "{object_address[1:]}" not found.'.encode(), {})
                
                        
#>>> import os.path
#>>> ext = os.path.splitext('/ak/52.png')

if __name__=="__main__":
    httpserver = HttpServer()
    d = httpserver.proses('GET testing.txt HTTP/1.0')
    print(d)
    d = httpserver.proses('GET donalbebek.jpg HTTP/1.0')
    print(d)
    #d = httpserver.http_get('testing2.txt',{})
    #print(d)
#   d = httpserver.http_get('testing.txt')
#   print(d)
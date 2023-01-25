#  coding: utf-8
import socketserver
# https://stackoverflow.com/questions/39090366/how-to-parse-raw-http-request-in-python-3
from email.parser import BytesParser
from email.utils import formatdate
import os.path
# Copyright 2013 Abram Hindle, Eddie Antonio Santos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/
# constants
TEXT_HTML = "text/html"
TEXT_CSS = "text/css"
CONTENT_TYPE = "Content-Type"


class MyWebServer(socketserver.BaseRequestHandler):

    def handle(self):

        data = self.request.recv(1024).strip()
        # print("Got a request of:\n%s\n" % data)
        # parse the GET request to get the status line and header as dictionaries
        statusLine, header = self.parseRequest(data)
        prefix = 'www'
        safepath = os.path.realpath(prefix)

        if (statusLine['method'] == "GET"):
            # prepend www to the requested path
            filepath = prefix + statusLine["path"]

            try:
                print(os.path.realpath(filepath))
                if os.path.commonprefix((os.path.realpath(filepath), safepath)) != safepath:
                    print("Invalid path!")
                    raise FileNotFoundError
                with open(filepath) as file:
                    self.serveFile(file, filepath)
            except FileNotFoundError:
                self.send404()
            except IsADirectoryError:
                if statusLine["path"][-1] != "/":
                    self.send301(
                        statusLine["path"]+'/')
                    return
                filepath += "index.html"
                with open(filepath) as file:
                    self.serveFile(file, filepath)
        else:
            self.send405()

    def parseRequest(self, data):
        lineDict = {}

        requestLine, headers = data.split(b'\r\n', 1)
        lineDict['method'], lineDict['path'], lineDict['ver'] = requestLine.decode('utf-8').split(
            " ")
        headerDict = BytesParser().parsebytes(headers)
        print(lineDict)
        body = {}
        return (lineDict, headerDict)

    def send301(self, path):
        print(301)
        self.sendResponse("301 Moved Permanently",
                          otherFields={"Location": path})

    def send404(self):
        print(404)
        message = "<!DOCTYPE html>\n<html>\n<body>\n<p>404 Not Found</p>\n</body>\n</html> \n"

        self.sendResponse("404 Not Found", body=message,
                          otherFields={CONTENT_TYPE: TEXT_HTML})

    def send405(self):
        print(405)
        self.sendResponse("405 Method Not Allowed")

    def serveFile(self, file, filePath):
        print("200")
        fileExt = filePath.split('.')[-1]
        print(fileExt)
        myType = ""
        if fileExt == 'html':
            myType = TEXT_HTML
        elif fileExt == 'css':
            myType = TEXT_CSS
        contents = file.read()

        self.sendResponse("200 OK", body=contents,
                          otherFields={CONTENT_TYPE: myType})

    def sendResponse(self, code, body="", otherFields={}):

        date = formatdate(usegmt=True)
        header = f"HTTP/1.1 {code}\r\nDate: {date}\r\n"
        if otherFields:
            for field, value in otherFields.items():
                header += f"{field}: {value}\r\n"
        rq = bytearray(header + "\r\n" + body, 'utf-8')
        # print(rq)
        self.request.sendall(rq)


if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

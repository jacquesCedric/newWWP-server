"""
Very simple HTTP server in python for logging requests
Usage::
    ./server.py [<port>]
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse
import os
import logging

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        # logging.info("POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
                # str(self.path), str(self.headers), post_data.decode('utf-8'))

        standard = post_data.decode("utf-8")
        dump = parse.parse_qs(standard)

        if "type" in dump.keys():
            if dump["type"][0] == "vote":
                writeVoteToFile(dump["titleID"][0])
            if dump["type"][0] == "chat":
                writeChatToFile(dump)


        self._set_response()

def run(server_class=HTTPServer, handler_class=S, port=3000):
    # logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    # logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    # logging.info('Stopping httpd...\n')

# Safety operations
def doesIDExist(titleID):
    with open("/resources/text/titleinfo.txt", "r") as f:
        for line in f:
            if line[8:16] == titleID[8:16]:
                return True
    return False

# Saving operations
def writeVoteToFile(titleID):
    if doesIDExist(titleID):
        with open("/resources/text/vote.txt", "a") as f:
            f.write(titleID + "\r")

        os.system("echo \"$(tail -n 200 /resources/text/vote.txt)\" > /resources/text/vote.txt")
    else:
        print("Could not write vote for: " + titleID)

def writeChatToFile(details):
    with open("/resources/text/msg.txt", "a") as f:
        f.write(details["author"][0] + ";;" + details["time"][0] + ";;" + details["message"][0] +"\r")

    os.system("echo \"$(tail -n 200 /resources/text/msg.txt)\" > /resources/text/msg.txt")


# Main function
if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
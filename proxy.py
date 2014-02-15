from socket import socket
from threading import Thread

class ProxyServerClientHandler(Thread):
    def __init__(self, client):
        self.inbound = client
        self.outbound = None
        self.requestParser = HTTPRequestParser()
        self.responseParser = 

    def hanlde(self):
        self.start()

    def run(self):


class ProxyServer:
    def __init__(self):
        self.socket = socket()
        self.socket.bind(("0.0.0.0", 1883))

    def serve_forever(self):
        self.socket.listen()
        while True:
            client, address = self.socket.accept()
            handler = ProxyServerClientHandler(client)
            handler.handle()
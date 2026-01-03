import socket
from src.resolver import DNSResolver

class UDPServer:
    def __init__(self, host, port, config):
        self.host = host
        self.port = port
        self.config = config
        self.sock = None
        self.running = False
        self.resolver = DNSResolver(config) 

    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.running = True
            print(f"[+] Server started on {self.host}:{self.port}")
            self._listen_loop()
        except Exception as e:
            print(f"[-] Error: {e}")
            self.stop()

    def _listen_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                self.handle_packet(data, addr)
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                print(f"[-] Receive Error: {e}")

    def handle_packet(self, data, addr):
        response_data = self.resolver.process_query(data, addr)
        
        if response_data:
            try:
                self.sock.sendto(response_data, addr)
            except Exception as e:
                print(f"[-] Send Error: {e}")

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
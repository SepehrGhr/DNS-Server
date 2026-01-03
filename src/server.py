import socket
from src.resolver import DNSResolver
import logging
import threading

class UDPServer:
    def __init__(self, host, port, config):
        self.host = host
        self.port = port
        self.config = config
        self.sock = None
        self.running = False
        self.logger = logging.getLogger(__name__)
        self.resolver = DNSResolver(config) 

    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((self.host, self.port))
            self.running = True
            self.logger.info(f"[+] Server started on {self.host}:{self.port}")
            self._listen_loop()
        except Exception as e:
            self.logger.error(f"[-] Error: {e}")
            self.stop()

    def _listen_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                client_thread = threading.Thread(
                    target=self.handle_packet,
                    args=(data, addr)
                )
                client_thread.daemon = True 
                client_thread.start()
            except KeyboardInterrupt:
                self.stop()
            except Exception as e:
                self.logger.error(f"[-] Receive Error: {e}")

    def handle_packet(self, data, addr):
        try:
            response_data = self.resolver.process_query(data, addr)
            if response_data:
                self.sock.sendto(response_data, addr)
        except Exception as e:
            self.logger.error(f"Handler Error: {e}")

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
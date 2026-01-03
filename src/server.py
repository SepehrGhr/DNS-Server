import socket
import sys

class UDPServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.running = False

    def start(self):
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((self.host, self.port))
            self.running = True
            print(f"[+] Server started on {self.host}:{self.port}")
            
            self._listen_loop()
        except PermissionError:
            print(f"[-] Error: Permission denied. Try using port > 1024 or run with sudo.")
        except OSError as e:
            print(f"[-] Error: {e}")
        finally:
            self.stop()

    def _listen_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(4096)
                
                self.handle_packet(data, addr)
                
            except KeyboardInterrupt:
                print("\n[*] Stopping server...")
                self.stop()
            except Exception as e:
                print(f"[-] Receive Error: {e}")

    def handle_packet(self, data, addr):
        print(f"[*] Received {len(data)} bytes from {addr}")

    def stop(self):
        self.running = False
        if self.sock:
            self.sock.close()
            print("[-] Socket closed.")
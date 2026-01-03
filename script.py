import socket
import json
import glob
from dnslib import DNSRecord, DNSHeader, RR, A, QTYPE, RCODE

IP = "127.0.0.1"  
PORT = 53 
ZONE_FILE = "zones.json"

def load_zones():
    """Loads the JSON file into a dictionary."""
    try:
        with open(ZONE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {ZONE_FILE} not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {ZONE_FILE}.")
        return {}

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        sock.bind((IP, PORT))
        print(f"[+] DNS Server started on {IP}:{PORT}")
        print(f"[+] specific records loaded from {ZONE_FILE}")
    except PermissionError:
        print(f"[-] Error: Permission denied. You need sudo/admin to bind to port {PORT}.")
        return

    while True:
        try:
            data, addr = sock.recvfrom(512)
            
            request = DNSRecord.parse(data)
            qname = str(request.q.qname)
            qtype = QTYPE[request.q.qtype]
            
            domain_lookup = qname.rstrip('.')

            print(f"Request: {domain_lookup} ({qtype}) from {addr}")

            reply = DNSRecord(DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)
            
            zones = load_zones()

            if domain_lookup in zones:
                ip_address = zones[domain_lookup]
                reply.add_answer(RR(
                    rname=qname,
                    rtype=QTYPE.A,
                    rclass=1,
                    ttl=60,
                    rdata=A(ip_address)
                ))
                print(f"  -> Found: {ip_address}")
            else:
                reply.header.rcode = RCODE.NXDOMAIN
                print(f"  -> Not Found")

            sock.sendto(reply.pack(), addr)

        except KeyboardInterrupt:
            print("\nShutting down server...")
            sock.close()
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    start_server()
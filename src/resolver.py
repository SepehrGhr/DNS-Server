import socket
from dnslib import DNSRecord, RCODE, QTYPE
from src.zones import ZoneManager

class DNSResolver:
    def __init__(self, config):
        self.config = config
        self.zonemanager = ZoneManager(config)
        self.upstream_ip = config["upstream_dns"]
        self.upstream_port = config["upstream_port"]

    def process_query(self, data, addr):
        try:
            request = DNSRecord.parse(data)
            qname = str(request.q.qname)
            qtype_int = request.q.qtype
            qtype_str = QTYPE[qtype_int]
            
            print(f"[*] Query: {qname} [{qtype_str}] from {addr}")

            reply = request.reply()
            answer_rr = self.zonemanager.get_record(qname, qtype_str)
            
            if answer_rr:
                print(f"    -> [Local Zone] Found: {answer_rr.rdata}")
                reply.add_answer(answer_rr)
                return reply.pack()

            print(f"    -> [Forwarding] Asking {self.upstream_ip}...")
            response_data = self._forward_query(data)
            
            if response_data:
                print(f"    -> [Forwarding] Success")
                return response_data
            
            print(f"    -> [Failure] Upstream timed out or failed")
            reply.header.rcode = RCODE.SERVFAIL
            return reply.pack()

        except Exception as e:
            print(f"[-] Resolver Error: {e}")
            return None

    def _forward_query(self, data):
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(2.0)
            
            sock.sendto(data, (self.upstream_ip, self.upstream_port))
            response, _ = sock.recvfrom(4096)
            return response
            
        except socket.timeout:
            return None 
        except Exception as e:
            print(f"[-] Forwarding Error: {e}")
            return None
        finally:
            if sock:
                sock.close()
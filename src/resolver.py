import socket
from dnslib import DNSRecord, RCODE, QTYPE, RR, PTR
import logging
from src.zones import ZoneManager
from src.cache import DNSCache  
from src.interceptor import DNSInterceptor

class DNSResolver:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.zonemanager = ZoneManager(config)
        self.cache = DNSCache()
        self.interceptor = DNSInterceptor()
        self.upstream_ip = config["upstream_dns"]
        self.upstream_port = config["upstream_port"]

    def process_query(self, data, addr):
        try:
            request = DNSRecord.parse(data)
            qname = str(request.q.qname)
            qtype_int = request.q.qtype
            qtype_str = QTYPE[qtype_int]
            
            self.logger.info(f"Query: {qname} [{qtype_str}] from {addr}")

            reply = request.reply()

            is_blocked, reason = self.interceptor.check_policy(qname)
            if is_blocked:
                self.logger.warning(f"    -> [BLOCKED] Domain: {qname} | Reason: {reason}")
                
                reply.header.rcode = RCODE.REFUSED
                return reply.pack()
            
            answer_rr = self.zonemanager.get_record(qname, qtype_str)
            if answer_rr:
                self.logger.info(f"    -> [Local Zone] Found")
                reply.add_answer(answer_rr)
                return reply.pack()

            cached_rr = self.cache.get(qname, qtype_str)
            if cached_rr:
                reply.add_answer(cached_rr)
                return reply.pack()
            
            self.logger.info(f"    -> [Forwarding] Asking {self.upstream_ip}...")
            response_data = self._forward_query(data)
            
            if response_data:
                upstream_response = DNSRecord.parse(response_data)
                if upstream_response.header.rcode == RCODE.NOERROR:
                    for rr in upstream_response.rr:
                        rname = str(rr.rname)
                        rtype = QTYPE[rr.rtype]
                        
                        if rname == qname and rtype == qtype_str:
                            self.cache.add(qname, qtype_str, rr, ttl=60)
                            self.logger.info(f"    -> [Cache] Stored {qname}")

                        if rtype == 'A':
                            try:
                                ip_str = str(rr.rdata)
                                reversed_ip = ".".join(reversed(ip_str.split('.')))
                                ptr_qname = f"{reversed_ip}.in-addr.arpa."
                                
                                ptr_rr = RR(
                                    rname=ptr_qname,
                                    rtype=QTYPE.PTR,
                                    rclass=1,
                                    ttl=60,
                                    rdata=PTR(rname)
                                )
                                
                                self.cache.add(ptr_qname, 'PTR', ptr_rr, ttl=60)
                                self.logger.info(f"    -> [Smart Cache] Learned Reverse: {ip_str} -> {rname}")
                                
                            except Exception as e:
                                self.logger.error(f"    [!] Auto-Reverse Error: {e}")

                return response_data
            
            reply.header.rcode = RCODE.SERVFAIL
            return reply.pack()

        except Exception as e:
            self.logger.error(f"[-] Resolver Error: {e}")
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
            self.logger.error(f"Forwarding Error: {e}")
            return None
        finally:
            if sock: sock.close()
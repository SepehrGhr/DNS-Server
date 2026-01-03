from dnslib import DNSRecord, RCODE, QTYPE
from src.zones import ZoneManager

class DNSResolver:
    def __init__(self, config):
        self.config = config
        self.zonemanager = ZoneManager(config) 

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
            
            print(f"    -> Not found locally")
            reply.header.rcode = RCODE.NXDOMAIN
            return reply.pack()

        except Exception as e:
            print(f"[-] Resolver Error: {e}")
            return None
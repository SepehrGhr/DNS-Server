from dnslib import DNSRecord, RCODE

class DNSResolver:
    def __init__(self, config):
        self.config = config

    def process_query(self, data, addr):

        try:
            request = DNSRecord.parse(data)
            qname = str(request.q.qname)
            qtype = request.q.qtype
            
            print(f"[*] Parsing Query: {qname} [{qtype}] from {addr}")

            reply = request.reply()
            
            reply.header.rcode = RCODE.NXDOMAIN

            return reply.pack()

        except Exception as e:
            print(f"[-] Resolver Error: {e}")
            return None
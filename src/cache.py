import time
import threading
from dnslib import DNSRecord, RR, QTYPE

class DNSCache:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()

    def get(self, qname, qtype):
        key = (qname, qtype)
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                expiry = entry['expiry']
                
                if time.time() < expiry:
                    print(f"    [Cache] Hit for {qname} [{qtype}]")
                    return entry['record']
                else:
                    print(f"    [Cache] Expired: {qname} [{qtype}]")
                    del self.cache[key]
        return None

    def add(self, qname, qtype, record, ttl=60):
        key = (qname, qtype)
        expiry = time.time() + ttl
        with self.lock:
            self.cache[key] = {
                'record': record,
                'expiry': expiry
            }
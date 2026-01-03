import time
import threading
import logging
from dnslib import DNSRecord, RR, QTYPE

class DNSCache:
    def __init__(self):
        self.cache = {}
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        self.cleaner_thread = threading.Thread(target=self._cleaner_loop, daemon=True)
        self.cleaner_thread.start()

    def get(self, qname, qtype):
        key = (qname, qtype)
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                if time.time() < entry['expiry']:
                    self.logger.info(f"    [Cache] Hit for {qname} [{qtype}]")
                    return entry['record']
                else:
                    self.logger.info(f"    [Cache] Expired (on access): {qname}")
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

    def _cleaner_loop(self):
            time.sleep(10)
            
            with self.lock:
                keys_to_check = list(self.cache.keys())
                now = time.time()
                count = 0
                
                for key in keys_to_check:
                    entry = self.cache.get(key)
                    if entry and now > entry['expiry']:
                        del self.cache[key]
                        count += 1
                
                if count > 0:
                    self.logger.info(f"    [Cache Janitor] Purged {count} expired records")
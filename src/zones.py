import json
import os
from dnslib import DNSRecord, RR, QTYPE, A, TXT, AAAA, PTR

class ZoneManager:
    def __init__(self, config):
        self.zone_file = os.path.join("config", "zones.json")
        self.zone_data = {}
        self.load_zones()

    def load_zones(self):
        try:
            with open(self.zone_file, 'r') as f:
                data = json.load(f)
                self.zone_data = {k.lower().rstrip('.') + '.': v for k, v in data.items()}
            print(f"[+] Loaded {len(self.zone_data)} zones from {self.zone_file}")
        except FileNotFoundError:
            print(f"[-] Warning: Zone file {self.zone_file} not found.")
            self.zone_data = {}
        except json.JSONDecodeError:
            print(f"[-] Error: Invalid JSON in {self.zone_file}.")

    def get_record(self, qname, qtype_str):
        key = qname.lower()
        
        if key in self.zone_data:
            records = self.zone_data[key]
            
            if qtype_str in records:
                value = records[qtype_str]
                
                if qtype_str == 'A':
                    return RR(rname=qname, rtype=QTYPE.A, rclass=1, ttl=300, rdata=A(value))
                elif qtype_str == 'AAAA':   
                    return RR(rname=qname, rtype=QTYPE.AAAA, rclass=1, ttl=300, rdata=AAAA(value))
                elif qtype_str == 'TXT':
                    return RR(rname=qname, rtype=QTYPE.TXT, rclass=1, ttl=300, rdata=TXT(value))
                elif qtype_str == 'PTR':
                    return RR(rname=qname, rtype=QTYPE.PTR, rclass=1, ttl=300, rdata=PTR(value))
        
        return None
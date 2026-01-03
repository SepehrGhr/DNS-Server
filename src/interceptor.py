import json
import os
import logging

class DNSInterceptor:
    def __init__(self):
        self.policy_file = os.path.join("config", "policies.json")
        self.rules = {}
        self.logger = logging.getLogger(__name__)
        self.load_policies()

    def load_policies(self):
        self.rules.clear()
        try:
            with open(self.policy_file, 'r') as f:
                data = json.load(f)
                for rule in data.get("rules", []):
                    domain = rule["domain"].lower().rstrip('.')
                    self.rules[domain] = rule
            self.logger.info(f"[+] Loaded {len(self.rules)} policy rules.")
        except FileNotFoundError:
            self.logger.warning(f"[-] Warning: Policy file not found at {self.policy_file}")
        except json.JSONDecodeError:
            self.logger.error(f"[-] Error: Invalid JSON in {self.policy_file}")
    def check_policy(self, qname):
        check_domain = qname.rstrip('.').lower()
        
        if check_domain in self.rules:
            return True, self.rules[check_domain]['reason']
        
        for domain, rule in self.rules.items():
            if check_domain.endswith("." + domain):
                return True, rule['reason']
                
        return False, None
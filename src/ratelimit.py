# src/ratelimit.py
import time
import threading
import logging

class RateLimiter:
    def __init__(self, limit=10, window=1.0):
        """
        limit: Max requests allowed
        window: Time window in seconds
        Example: 10 requests per 1 second
        """
        self.limit = limit
        self.window = window
        self.clients = {}
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)

    def is_allowed(self, ip):
        current_time = time.time()
        with self.lock:
            if ip not in self.clients:
                self.clients[ip] = []
            
            timestamps = self.clients[ip]
            valid_timestamps = [t for t in timestamps if current_time - t < self.window]
            
            if len(valid_timestamps) < self.limit:
                valid_timestamps.append(current_time)
                self.clients[ip] = valid_timestamps
                return True
            else:
                return False
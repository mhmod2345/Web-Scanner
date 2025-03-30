#!/usr/bin/env python3
"""
Mahmod Mhagne's Ultimate Web Scanner - V6.0
"""

import requests
import argparse
import time
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

class UltimateScanner:
    def __init__(self, base_url, wordlist_file, max_threads=100):
        self.base_url = base_url.rstrip('/')
        self.wordlist_file = wordlist_file
        self.max_threads = max_threads
        self.found = []
        self.scanned = 0
        self.start_time = None
        
        # Session settings
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'MahmodScanner/6.0',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        self.timeout = 8
        
        # Statistics
        self.total_paths = self.count_lines()

    def show_banner(self):
        """Custom banner with your name"""
        print(f"""
\033[1;36m
╔╦╗╔═╗╦  ╔╗ ┌─┐┌─┐┌┐┌┌─┐┬─┐  ╔╦╗╔═╗╔╗╔╔╦╗╦ ╦╔═╗
║║║╠═╣║  ╠╩╗├┤ ├─┤│││├┤ ├┬┘  ║║║╠═╣║║║ ║ ║ ║╚═╗
╩ ╩╩ ╩╩═╝╚═╝└─┘┴ ┴┘└┘└─┘┴└─  ╩ ╩╩ ╩╝╚╝ ╩ ╚═╝╚═╝
\033[0m
\033[1;35mDeveloper: Mahmod Mhagne
Version: Ultimate Scanner V6.0
\033[0m
\033[1;33mTarget: \033[0m{self.base_url}
\033[1;33mWordlist: \033[0m{os.path.basename(self.wordlist_file)} ({self.total_paths:,} paths)
\033[1;33mThreads: \033[0m{self.max_threads}
\033[1;33mTimeout: \033[0m{self.timeout}s
\033[1;31m"Excellence in performance, precision in results"\033[0m
""")

    def count_lines(self):
        """Count paths in wordlist"""
        with open(self.wordlist_file, 'rb') as f:
            return sum(1 for _ in f)

    def load_wordlist(self):
        """Load wordlist efficiently"""
        with open(self.wordlist_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                yield line.strip()

    def scan_path(self, path):
        """Scan a single path"""
        try:
            url = f"{self.base_url}/{path.lstrip('/')}"
            response = self.session.head(
                url,
                timeout=self.timeout,
                allow_redirects=False
            )
            
            if response.status_code in (200, 403, 401, 500):
                size = self.get_size(response)
                return {
                    'url': url,
                    'status': response.status_code,
                    'size': size,
                    'path': path
                }
                
        except:
            return None
        finally:
            self.scanned += 1
            self.update_progress()

    def get_size(self, response):
        """Get human-readable size"""
        try:
            size = int(response.headers.get('Content-Length', 0))
            if size >= 1024*1024:
                return f"{size/(1024*1024):.1f}MB"
            elif size >= 1024:
                return f"{size/1024:.1f}KB"
            return f"{size}B"
        except:
            return "N/A"

    def update_progress(self):
        """Update progress bar"""
        if self.scanned % 100 == 0 or self.scanned == self.total_paths:
            elapsed = time.time() - self.start_time
            speed = self.scanned / max(elapsed, 1)
            sys.stdout.write(
                f"\r\033[KProgress: {self.scanned}/{self.total_paths} "
                f"({speed:.1f} req/s) | "
                f"Found: {len(self.found)}"
            )
            sys.stdout.flush()

    def print_result(self, result):
        """Print results in requested format"""
        colors = {
            200: '\033[92m',  # Green
            403: '\033[93m',  # Yellow
            401: '\033[96m',  # Cyan
            500: '\033[91m'   # Red
        }
        color = colors.get(result['status'], '\033[0m')
        print(f"{color}★ {result['status']} {result['url']} (Size: {result['size']})\033[0m")

    def run_scan(self):
        """Start scanning process"""
        self.start_time = time.time()
        self.show_banner()
        print("\033[1;33m" + "="*60 + "\033[0m")
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            futures = {
                executor.submit(self.scan_path, path): path 
                for path in self.load_wordlist()
            }
            
            for future in as_completed(futures):
                if result := future.result():
                    self.found.append(result)
                    self.print_result(result)
        
        self.save_results()

    def save_results(self):
        """Save scan results"""
        if not self.found:
            print("\n\033[1;33m[!] No findings detected\033[0m")
            return
            
        if not os.path.exists('scans'):
            os.makedirs('scans')
            
        filename = f"scans/{self.base_url.replace('://', '_')}_{time.strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Scan Results - Mahmod Mhagne Scanner V6.0\n")
            f.write(f"Target: {self.base_url}\n")
            f.write(f"Date: {time.ctime()}\n")
            f.write(f"Paths Tested: {self.total_paths}\n")
            f.write(f"Findings: {len(self.found)}\n\n")
            
            for item in self.found:
                f.write(f"{item['status']} {item['url']} (Size: {item['size']})\n")
        
        print("\n\033[1;32m" + "="*60)
        print(f"[+] Scan completed in {time.time()-self.start_time:.2f}s")
        print(f"[+] Total findings: {len(self.found)}")
        print(f"[+] Results saved to {filename}")
        print("="*60 + "\033[0m")

def show_help():
    """Custom help menu with your name"""
    print(f"""
\033[1;36m
╔╦╗╔═╗╦  ╔╗ ┌─┐┌─┐┌┐┌┌─┐┬─┐  ╔╦╗╔═╗╔╗╔╔╦╗╦ ╦╔═╗
║║║╠═╣║  ╠╩╗├┤ ├─┤│││├┤ ├┬┘  ║║║╠═╣║║║ ║ ║ ║╚═╗
╩ ╩╩ ╩╩═╝╚═╝└─┘┴ ┴┘└┘└─┘┴└─  ╩ ╩╩ ╩╝╚╝ ╩ ╚═╝╚═╝
\033[0m
\033[1;35mDeveloper: Mahmod Mhagne
Version: Ultimate Scanner V6.0
\033[0m
Usage: python scanner.py -u URL -w WORDLIST [options]

Required Arguments:
  -u URL, --url URL     Target URL to scan (e.g., https://example.com)
  -w WORDLIST, --wordlist WORDLIST
                        Path to wordlist file

Options:
  -t THREADS, --threads THREADS
                        Number of threads (default: 100)
  -h, --help            Show this help message

Examples:
  python scanner.py -u https://example.com -w paths.txt
  python scanner.py -u https://example.com -w ~/wordlists/big.txt -t 150
""")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-u', '--url', help='Target URL to scan')
    parser.add_argument('-w', '--wordlist', help='Path to wordlist file')
    parser.add_argument('-t', '--threads', type=int, default=100, help='Number of threads')
    parser.add_argument('-h', '--help', action='store_true', help='Show help')

    args = parser.parse_args()

    if args.help or not args.url or not args.wordlist:
        show_help()
        return

    try:
        scanner = UltimateScanner(args.url, args.wordlist, args.threads)
        scanner.run_scan()
    except KeyboardInterrupt:
        print("\n\033[1;33m[!] Scan interrupted by user\033[0m")
    except Exception as e:
        print(f"\033[1;31m[!] Error: {str(e)}\033[0m")
    finally:
        print("\n\033[1;35m[+] Scanner by Mahmod Mhagne - Happy hunting!\033[0m")

if __name__ == "__main__":
    main()
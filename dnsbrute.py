import dns.resolver
from dns.resolver import NXDOMAIN, NoAnswer, Timeout
from datetime import datetime
import concurrent.futures

# Get user input for wordlist and target
wordlist_path = input("Enter the path to the wordlist file: ")
target = input("Enter the target domain: ")

# Resolver configuration
res = dns.resolver.Resolver()
res.timeout = 5
res.lifetime = 10

# Load subdomains from file
try:
    with open(wordlist_path, "r") as file:
        subdomains = file.read().splitlines()
except FileNotFoundError:
    print(f"[Error] The file {wordlist_path} was not found.")
    exit(1)

total_subdomains = len(subdomains)
found_subdomains = []

print(f"[*] Starting to check {total_subdomains} subdomains for target {target}")

# Function to resolve subdomains
def resolve_subdomain(subdomain):
    sub_target = f"{subdomain}.{target}"
    try:
        result = res.resolve(sub_target, "A")
        for ip in result:
            return f"{sub_target} -> {ip}"
    except NXDOMAIN:
        return f"[NXDOMAIN] Subdomain {sub_target} does not exist."
    except NoAnswer:
        return f"[NoAnswer] Subdomain {sub_target} has no A records."
    except Timeout:
        return f"[Timeout] Timed out while trying to resolve {sub_target}."
    except Exception as e:
        return f"[Error] Failed to resolve {sub_target}: {e}"

# Use a thread pool to parallelize the resolution
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    future_to_subdomain = {executor.submit(resolve_subdomain, subdomain): subdomain for subdomain in subdomains}
    for i, future in enumerate(concurrent.futures.as_completed(future_to_subdomain), 1):
        result = future.result()
        if "->" in result:
            found_subdomains.append(result)
        print(f"[{i}/{total_subdomains}] {result}")

# Summary of results
print("\n[*] Scan completed.")
print(f"[*] Found {len(found_subdomains)} subdomains with valid A records:")
for found in found_subdomains:
    print(f"    - {found}")
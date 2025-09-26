import ipaddress
import math
import requests
import json

def load_config(file_path="config.json"):
    with open(file_path) as f:
        return json.load(f)

config = load_config()
NETBOX_URL = config["NETBOX_URL"]
NETBOX_TOKEN = config["NETBOX_TOKEN"]

HEADERS = {
    "Authorization": f"Token {NETBOX_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

class NetBoxAllocator:
    def __init__(self, parent_prefix):
        self.parent_prefix = ipaddress.ip_network(parent_prefix)
        self.allocated_subnets = self._get_allocated_prefixes()

    def _get_allocated_prefixes(self):
        #Fetch already allocated prefixes from NetBox for this parent pool
        url = f"{NETBOX_URL}/ipam/prefixes/?within={self.parent_prefix}"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        return [ipaddress.ip_network(r["prefix"]) for r in data["results"]]

    def _required_prefix(self, num_hosts):
        #Calculate prefix length that can hold num_hosts
        required = num_hosts + 2  # network + broadcast
        bits_needed = math.ceil(math.log2(required))
        return 32 - bits_needed

    def allocate(self, customer_name, num_hosts):
        #Allocate a new prefix if space available, push to NetBox
        prefix_len = self._required_prefix(num_hosts)
        candidate_subnets = list(self.parent_prefix.subnets(new_prefix=prefix_len))

        for subnet in candidate_subnets:
            if all(not subnet.overlaps(alloc) for alloc in self.allocated_subnets):
                # Safe to allocate
                payload = {
                    "prefix": str(subnet),
                    "description": f"Allocated to {customer_name}",
                    "status": "active"
                }
                url = f"{NETBOX_URL}/ipam/prefixes/"
                resp = requests.post(url, headers=HEADERS, json=payload)

                if resp.status_code == 201:
                    print(f"Allocated {subnet} to {customer_name}")
                    self.allocated_subnets.append(subnet)
                    return subnet
                else:
                    print("NetBox error:", resp.text)
                    return None

        print("No available space for this request.")
        return None

    def view_allocations(self, customer_name):
        #Fetch and display allocations for a specific customer
        url = f"{NETBOX_URL}/ipam/prefixes/?q={customer_name}"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()

        if not data["results"]:
            print(f"No allocations found for {customer_name}")
            return

        print(f"\nAllocations for {customer_name}:")
        for r in data["results"]:
            print(f"- {r['prefix']} ({r['description']})")

    def deallocate(self, prefix_str):
        #Delete or shrink a subnet allocation in NetBox
        # Find prefix ID from NetBox
        url = f"{NETBOX_URL}/ipam/prefixes/?prefix={prefix_str}"
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()

        if not data["results"]:
            print("Prefix not found in NetBox.")
            return

        prefix_id = data["results"][0]["id"]

        # Delete prefix
        del_url = f"{NETBOX_URL}/ipam/prefixes/{prefix_id}/"
        del_resp = requests.delete(del_url, headers=HEADERS)

        if del_resp.status_code == 204:
            print(f"Deallocated {prefix_str}")
            # Remove from local memory too
            self.allocated_subnets = [p for p in self.allocated_subnets if str(p) != prefix_str]
        else:
            print("Failed to delete prefix:", del_resp.text)


def main():
    allocator = NetBoxAllocator("192.168.0.0/16")

    while True:
        print("\n========= IP Allocation Menu =========")
        print("1. Add new prefix")
        print("2. View customer allocations")
        print("3. Deallocate a subnet")
        print("4. Exit")
        print("======================================")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            customer = input("Enter customer name: ").strip()
            hosts = int(input("Enter number of hosts required: ").strip())
            allocator.allocate(customer, hosts)

        elif choice == "2":
            customer = input("Enter customer name to search: ").strip()
            allocator.view_allocations(customer)

        elif choice == "3":
            prefix = input("Enter subnet prefix to deallocate (e.g. 192.168.0.0/23): ").strip()
            allocator.deallocate(prefix)

        elif choice == "4":
            print("Exiting...")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    main()

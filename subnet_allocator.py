import ipaddress
import math
import csv

class IPAllocator:
    def __init__(self, base_network):
        self.base_network = ipaddress.ip_network(base_network)
        self.allocated_subnets = []

    def _required_prefix(self, num_hosts):
        #Calculate the prefix length for a subnet that can fit num_hosts
        required = num_hosts + 2 
        bits_needed = math.ceil(math.log2(required))
        prefix_length = 32 - bits_needed
        return prefix_length

    def allocate(self, num_hosts):
        prefix = self._required_prefix(num_hosts)
        candidate_subnets = list(self.base_network.subnets(new_prefix=prefix))

        for subnet in candidate_subnets:
            if all(not subnet.overlaps(alloc) for alloc in self.allocated_subnets):
                self.allocated_subnets.append(subnet)
                return subnet

        return None 


def allocate_from_csv(base_network, input_csv, output_csv):
    allocator = IPAllocator(base_network)

    results = []
    with open(input_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            customer = row["customer_name"]
            hosts = int(row["num_hosts"])
            subnet = allocator.allocate(hosts)
            results.append({
                "customer_name": customer,
                "num_hosts": hosts,
                "allocated_subnet": str(subnet) if subnet else "NOT AVAILABLE"
            })

    with open(output_csv, "w", newline='') as csvfile:
        fieldnames = ["customer_name", "num_hosts", "allocated_subnet"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for r in results:
            writer.writerow(r)

    print(f"Allocation results saved to {output_csv}")


if __name__ == "__main__":
    allocate_from_csv("10.0.0.0/8", "requests.csv", "allocations.csv")

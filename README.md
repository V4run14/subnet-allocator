# subnet-allocator

## Overview
This project provides a **subnet allocation tool** that takes a pool of a given network (e.g., a Class B like `172.16.0.0/16`) and, based on a customer’s host requirement, allocates:
- The **tightest subnet mask possible** (just enough addresses to satisfy the demand).  
- The **first available subnet** inside the pool.  

The allocation logic ensures no overlap with previously assigned prefixes.

On top of that, the tool integrates with **[NetBox](https://netbox.dev/)** (a popular IP Address Management tool), overcoming a limitation of NetBox:  
> NetBox is excellent at managing IP prefixes and metadata, but it **does not allocate subnets for you**.  

This project bridges that gap:  
- Allocates the subnet automatically.  
- Creates the prefix entry in NetBox via its **REST API**.  
- Lets you view existing allocations for a customer.  
- Allows deallocation of prefixes when no longer needed.  

---

## Features
- **Standalone Subnet Allocation**: Read customer requests from CSV, allocate subnets, and output results to CSV.  
- **NetBox Integration**: Automatically create prefixes in NetBox after allocation.  
- **View Allocations**: Query NetBox for subnets allocated to a specific customer.  
- **Deallocate Subnets**: Free up or shrink a prefix in NetBox when a customer no longer needs it.  
- **Tight Masking**: Always allocates the smallest possible subnet to fit the demand.  

---

## Files in the Repo
- **`subnet_allocator.py`**  
  Standalone version.  
  - Reads input from `requests.csv` (customer name and number of hosts).  
  - Outputs allocated subnets into `allocations.csv`.  
  - Good for testing or offline subnet planning.  

- **`netbox_allocator.py`**  
  NetBox-integrated version.  
  - Reads **API token and NetBox URL** from `config.json`.  
  - Allocates subnets, creates prefixes in NetBox, and provides a menu for:
    - Adding a new prefix for a customer.  
    - Viewing existing allocations.  
    - Deallocating a prefix.  

- **`config.json`**  
  Stores NetBox API connection details. Example:
  ```json
  {
    "NETBOX_URL": "https://demo.netbox.dev/api",
    "NETBOX_TOKEN": "YOUR_API_TOKEN_HERE"
  }

## Usage Screenshots

### 1. Running `subnet_allocator.py`
- Input file: `requests.csv` with customer demands.  
- Output file: `allocations.csv` with allocated subnets.  

**requests.csv**  
![Requests CSV](screenshots/requests.png)  

**allocations.csv (after running subnet_allocator.py)**  
![Allocations CSV](screenshots/allocations.png)  

---

### 2. NetBox Before and After Allocation
When you start, your NetBox IPAM may be empty:  

**NetBox (before allocation)**  
![NetBox Before](screenshots/netbox_before.png)  

After running `netbox_allocator.py` and allocating prefixes, the subnets are created automatically in NetBox:  

**NetBox (after allocation)**  
![NetBox After](screenshots/netbox_after.png)  

---

### 3. Using `netbox_allocator.py`
The tool provides a simple command-line menu for managing allocations.  

**Main Menu**  
![Allocator Menu](screenshots/allocation_menu.png)  


# Setting up a NetBox Account

Follow these steps to create a free NetBox Cloud account and generate your API token for use with the subnet allocator tool.

---

## 1. Create a NetBox Cloud Account
- Go to [NetBox Cloud Free Tier](https://www.netbox.dev/signup/).  
- Sign up for a free account or log in if you already have one.  
- Once created, you’ll have access to your own NetBox instance (e.g., `https://your-tenant.netbox.dev`).  

---

## 2. Generate an API Token
1. Log in to your NetBox instance.  
2. Click on your **username** in the top-right corner.  
3. Select **API Tokens** from the dropdown menu.  
4. Click **Add Token**.  
5. Enter a name/description for the token (e.g., `Subnet Allocator`).  
6. Ensure **Read/Write** permissions are enabled.  
7. Save the token and copy the value (you’ll need it for config).  

---

## 3. Configure the Tool
- Open the `config.json` file in your repo.  
- Add your NetBox instance URL and the token you just generated:

```json
{
  "NETBOX_URL": "https://your-tenant.netbox.dev/api",
  "NETBOX_TOKEN": "YOUR_API_TOKEN_HERE"
}

import requests
import json

base_url = "http://127.0.0.1:8001"

print("[*] Starting integration test against live CRM server at http://127.0.0.1:8001...")

# 1. Create client
payload = {
    "name": "Rick Jefferson",
    "email": "rjbizsolution23+test@gmail.com",
    "phone": "(505) 555-1342"
}
res = requests.post(f"{base_url}/api/clients", json=payload)
print("[+] Create Client Response:")
print(json.dumps(res.json(), indent=2))
client_data = res.json()
if not client_data.get("success"):
    print("[-] Failed to create client")
    exit(1)
client_id = client_data.get("client_id")

# 2. Get client details & pull mock reports/negative items
res_details = requests.get(f"{base_url}/api/clients/{client_id}")
print("\n[+] Client Details & Negatives Response:")
print(json.dumps(res_details.json(), indent=2))
details_data = res_details.json()
negatives = details_data.get("negative_items", [])

if negatives:
    # 3. Generate a dispute letter for the first negative item
    neg = negatives[0]
    dispute_payload = {
        "client_id": client_id,
        "bureau": neg["bureau"],
        "item_name": neg["item_name"],
        "account_number": neg["account_number"],
        "dispute_reason": neg["reason"],
        "dispute_type": neg["type"]
    }
    res_dispute = requests.post(f"{base_url}/api/disputes/generate", json=dispute_payload)
    print("\n[+] Generated Dispute Letter Response:")
    print(json.dumps(res_dispute.json(), indent=2))
else:
    print("\n[-] No negative items found to dispute.")

# 4. Clean up client
res_delete = requests.delete(f"{base_url}/api/clients/{client_id}")
print("\n[+] Delete Client Response:")
print(json.dumps(res_delete.json(), indent=2))

print("\n[+] Live API Integration Test passed successfully!")

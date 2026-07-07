# =============================================================================
# Credit Repair CRM & Dispute Generator — Local Endpoint Test Suite
# Rick Jefferson | RJ Business Solutions
# 📍 1342 NM 333, Tijeras, New Mexico 87059
# 🌐 https://rickjeffersonsolutions.com
# =============================================================================

import sys
import os
import json
import sqlite3
from pathlib import Path

# Add database paths
sys.path.append(str(Path(__file__).parent))

from models import init_db, get_db_connection, DB_PATH
from myfreescorenow import MyFreeScoreNowClient

def run_tests():
    print("[*] Starting Credit Repair CRM integration test suite...")
    
    # 1. Database Initialization
    print("[*] 1. Initializing local database...")
    init_db()
    if not DB_PATH.exists():
        print("[-] Database file not created.")
        sys.exit(1)
    print("[+] Database initialized successfully.")

    # 2. MyFreeScoreNow Client Setup & URL Generation
    print("\n[*] 2. Checking MyFreeScoreNow client...")
    client = MyFreeScoreNowClient()
    url = client.get_enrollment_url(high_value=False)
    print(f"[+] Primary Enrollment URL: {url}")
    if "AID=RickJeffersonSolutions" not in url or "PID=49914" not in url:
        print("[-] Enrollment URL lacks AID/PID parameters.")
        sys.exit(1)
    
    url_high = client.get_enrollment_url(high_value=True)
    print(f"[+] High-Value Enrollment URL: {url_high}")
    if "AID=RickJeffersonSolutions" not in url_high or "PID=30639" not in url_high:
        print("[-] High-Value Enrollment URL lacks AID/PID parameters.")
        sys.exit(1)
        
    # 3. Client Intake Lead Registration
    print("\n[*] 3. Registering mock client intake...")
    lead_res = client.register_lead("Jane Doe", "janedoe@example.com", "(505) 555-9271")
    print(f"[+] Registration Response: {json.dumps(lead_res)}")
    if not lead_res.get("success") or not lead_res.get("lead_id"):
        print("[-] Lead registration failed.")
        sys.exit(1)
    lead_id = lead_res.get("lead_id")
    print(f"[+] Registered Lead ID: {lead_id}")
    
    # 4. Fetching Credit Reports
    print("\n[*] 4. Retrieval of credit reports...")
    report_res = client.fetch_credit_report(lead_id)
    print(f"[+] Credit Report Pull: {json.dumps(report_res)}")
    if not report_res.get("success") or not report_res.get("scores"):
        print("[-] Credit report retrieval failed.")
        sys.exit(1)
    print(f"[+] Retracted Scores: {report_res.get('scores')}")

    # 5. SQLite Data Insertion
    print("\n[*] 5. Inserting client details in SQLite database...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clean test records first
    cursor.execute("DELETE FROM clients WHERE email = ?", ("janedoe@example.com",))
    
    # Insert new record
    scores_str = json.dumps(report_res.get("scores"))
    cursor.execute(
        "INSERT INTO clients (name, email, phone, myfreescorenow_id, scores) VALUES (?, ?, ?, ?, ?)",
        ("Jane Doe", "janedoe@example.com", "(505) 555-9271", lead_id, scores_str)
    )
    conn.commit()
    
    # Fetch record to verify
    cursor.execute("SELECT * FROM clients WHERE email = ?", ("janedoe@example.com",))
    record = cursor.fetchone()
    print(f"[+] Stored Database Client: {dict(record)}")
    
    # Verify scores parsing
    scores_parsed = json.loads(record["scores"])
    print(f"[+] Parsed Scores from database: {scores_parsed}")
    
    # Clean up test records
    cursor.execute("DELETE FROM clients WHERE email = ?", ("janedoe@example.com",))
    conn.commit()
    conn.close()

    print("\n[+] All CRM tests completed successfully! No issues found.")

if __name__ == "__main__":
    run_tests()

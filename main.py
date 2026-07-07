# =============================================================================
# Credit Repair CRM & Dispute Generator — FastAPI Backend Controller
# Rick Jefferson | RJ Business Solutions
# 📍 1342 NM 333, Tijeras, New Mexico 87059
# 🌐 https://rickjeffersonsolutions.com
# =============================================================================

import os
import json
import sqlite3
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from models import init_db, get_db_connection, DB_PATH
from myfreescorenow import MyFreeScoreNowClient
import requests

app = FastAPI(title="RJ Credit Repair CRM & Dispute Generator")

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Resolve paths
STATIC_PATH = os.path.dirname(os.path.abspath(__file__)) + "/static"
os.makedirs(STATIC_PATH, exist_ok=True)

# Bureau official dispute addresses
BUREAU_ADDRESSES = {
    "Experian": "Experian Information Solutions\nP.O. Box 4500\nAllen, TX 75013",
    "TransUnion": "TransUnion Consumer Solutions\nP.O. Box 2000\nChester, PA 19016",
    "Equifax": "Equifax Information Services LLC\nP.O. Box 740256\nAtlanta, GA 30374"
}

# =============================================================================
# PYDANTIC SCHEMAS
# =============================================================================

class ClientCreate(BaseModel):
    name: str
    email: str
    phone: str

class DisputeGenerateRequest(BaseModel):
    client_id: int
    bureau: str
    item_name: str
    account_number: str
    dispute_reason: str
    dispute_type: str # Collection, Late Payment, Charge Off, Inquiry

class EmailLetterRequest(BaseModel):
    client_id: int
    to_email: str
    bureau: str
    subject: str
    body: str

# =============================================================================
# API ROUTES
# =============================================================================

@app.get("/api/clients")
def get_clients():
    """Retrieve all clients in the CRM."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients ORDER BY created_at DESC")
    rows = cursor.fetchall()
    clients = []
    for row in rows:
        clients.append({
            "id": row["id"],
            "name": row["name"],
            "email": row["email"],
            "phone": row["phone"],
            "myfreescorenow_id": row["myfreescorenow_id"],
            "scores": json.loads(row["scores"]),
            "status": row["status"],
            "created_at": row["created_at"]
        })
    conn.close()
    return clients

@app.post("/api/clients")
def create_client(client: ClientCreate):
    """Create a new client in the CRM and register them with MyFreeScoreNow."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Register lead with MyFreeScoreNow first
    mfsn = MyFreeScoreNowClient()
    lead_res = mfsn.register_lead(client.name, client.email, client.phone)
    lead_id = lead_res.get("lead_id") if lead_res.get("success") else None
    
    try:
        cursor.execute(
            "INSERT INTO clients (name, email, phone, myfreescorenow_id) VALUES (?, ?, ?, ?)",
            (client.name, client.email, client.phone, lead_id)
        )
        conn.commit()
        client_id = cursor.lastrowid
        conn.close()
        return {
            "success": True,
            "client_id": client_id,
            "myfreescorenow_id": lead_id,
            "enrollment_url": mfsn.get_enrollment_url(),
            "message": "Client created successfully in CRM."
        }
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Client with this email already exists.")
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/clients/{client_id}")
def get_client_details(client_id: int):
    """Retrieve details of a single client, including their credit score reports."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Client not found.")
        
    client_data = {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "phone": row["phone"],
        "myfreescorenow_id": row["myfreescorenow_id"],
        "scores": json.loads(row["scores"]),
        "status": row["status"],
        "created_at": row["created_at"]
    }
    
    # Fetch report items if myfreescorenow ID exists
    negative_items = []
    if client_data["myfreescorenow_id"]:
        mfsn = MyFreeScoreNowClient()
        report_res = mfsn.fetch_credit_report(client_data["myfreescorenow_id"])
        if report_res.get("success"):
            negative_items = report_res.get("negative_items", [])
            # Dynamic score synchronization
            if report_res.get("scores"):
                scores_str = json.dumps(report_res.get("scores"))
                cursor.execute("UPDATE clients SET scores = ? WHERE id = ?", (scores_str, client_id))
                conn.commit()
                client_data["scores"] = report_res.get("scores")
                
    conn.close()
    return {
        "client": client_data,
        "negative_items": negative_items
    }

@app.delete("/api/clients/{client_id}")
def delete_client(client_id: int):
    """Deletes a client from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Client deleted successfully."}

@app.post("/api/disputes/generate")
def generate_dispute_letter(req: DisputeGenerateRequest):
    """Generates a print-ready dispute letter using credit dispute templates."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clients WHERE id = ?", (req.client_id,))
    client = cursor.fetchone()
    if not client:
        conn.close()
        raise HTTPException(status_code=404, detail="Client not found.")

    bureau_addr = BUREAU_ADDRESSES.get(req.bureau, "Credit Bureau Services")
    
    # Select dispute body text based on dispute type
    if req.dispute_type.lower() == "collection":
        body_text = (
            f"I am disputing the collection account reported under the name {req.item_name} "
            f"and account number {req.account_number}. This collection is reporting inaccurate, "
            f"unverified details. I request full validation of this debt from the original creditor, "
            f"including the signed copy of the contract. If no physical signed agreement is found, "
            f"this item must be deleted from my file immediately."
        )
    elif req.dispute_type.lower() == "late payment":
        body_text = (
            f"I am disputing the late payment status reported on my account with {req.item_name} "
            f"(Account: {req.account_number}). I have consistently made timely payments. Please verify "
            f"the billing ledger logs. Any undocumented late payment reports violate the Fair Credit "
            f"Reporting Act and must be removed."
        )
    elif req.dispute_type.lower() == "charge off":
        body_text = (
            f"I am disputing the charge-off status reported on the account {req.item_name} "
            f"with account number {req.account_number}. The balance amount and payment histories are "
            f"incorrect. Under the FCRA, all reported balances must be accurate and validated. Please "
            f"remove this charge-off notation."
        )
    else: # Inquiry or general dispute
        body_text = (
            f"I am disputing the unauthorized inquiry listed on my report by {req.item_name} "
            f"on account/reference number {req.account_number}. I did not authorize this inquiry, "
            f"and it violates my credit privacy rights. Please remove this inquiry from my file."
        )

    # Inject dispute reason
    body_text += f"\n\nDispute Reason: {req.dispute_reason}"

    # Build the full dispute letter
    letter_content = f"""Date: [Current Date]

To:
{bureau_addr}

From:
{client['name']}
Email: {client['email']}
Phone: {client['phone']}

RE: Dispute of Inaccurate Credit Information (Account: {req.account_number})

To Whom It May Concern,

I am writing to formally dispute the following inaccurate information appearing on my credit report:

Creditor/Agency: {req.item_name}
Account Number: {req.account_number}
Dispute Type: {req.dispute_type}

{body_text}

Under Section 611 of the Fair Credit Reporting Act (15 U.S.C. § 1681i), you are required to investigate my dispute within 30 days and notify me of the results. Please update my report accordingly.

Sincerely,

{client['name']}
"""

    # Log dispute item in database
    cursor.execute(
        "INSERT INTO disputes (client_id, bureau, item_name, account_number, dispute_reason, status, letter_text) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (req.client_id, req.bureau, req.item_name, req.account_number, req.dispute_reason, "Pending", letter_content)
    )
    conn.commit()
    conn.close()

    return {
        "success": True,
        "bureau": req.bureau,
        "bureau_address": bureau_addr,
        "client_name": client["name"],
        "letter_content": letter_content
    }

@app.post("/api/disputes/email")
def email_dispute_letter(req: EmailLetterRequest):
    """Sends the generated dispute letter to the client's email using Resend API."""
    resend_key = os.getenv("RESEND_API_KEY")
    if not resend_key:
        raise HTTPException(status_code=500, detail="Resend email service is not configured on server.")

    url = "https://api.resend.com/emails"
    headers = {
        "Authorization": f"Bearer {resend_key}",
        "Content-Type": "application/json"
    }
    
    # Format the letter content with double carriage returns for HTML email
    formatted_body = req.body.replace("\n", "<br>")
    
    payload = {
        "from": "Credit Repair Swarm <onboarding@resend.dev>",
        "to": req.to_email,
        "subject": req.subject,
        "html": f"""
        <h3>RJ Business Solutions — Client Credit Repair Dashboard</h3>
        <p>Dear Client, here is your generated dispute letter ready for bureau submission:</p>
        <hr>
        <div style="font-family: monospace; white-space: pre-wrap; background: #f8fafc; padding: 15px; border: 1px solid #e2e8f0;">
        {formatted_body}
        </div>
        <hr>
        <p>📍 1342 NM 333, Tijeras, New Mexico 87059 | 🌐 <a href="https://rickjeffersonsolutions.com">rickjeffersonsolutions.com</a></p>
        """
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=20)
        if res.status_code in [200, 201]:
            return {"success": True, "message": f"Dispute letter successfully emailed to {req.to_email}"}
        return {"success": False, "error": f"Failed to send email. Resend response: {res.text}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Serving UI
@app.get("/")
def get_index():
    return FileResponse(STATIC_PATH + "/index.html")

# Mount Static Assets
app.mount("/", StaticFiles(directory=STATIC_PATH), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)

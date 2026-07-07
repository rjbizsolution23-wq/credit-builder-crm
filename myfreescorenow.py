# =============================================================================
# Credit Repair CRM — MyFreeScoreNow API Integration Service
# Rick Jefferson | RJ Business Solutions
# 📍 1342 NM 333, Tijeras, New Mexico 87059
# 🌐 https://rickjeffersonsolutions.com
# =============================================================================

import os
import requests
from dotenv import load_dotenv

load_dotenv()

# Mandatory API credentials
API_BASE_URL = "https://api.myfreescorenow.com/api"
AFFILIATE_AID = "RickJeffersonSolutions"
PID_PRIMARY = "49914"      # $29.90/mo | 7-day $1 trial
PID_HIGH_VALUE = "30639"   # $39.90/mo | no trial

class MyFreeScoreNowClient:
    def __init__(self):
        # Read credentials securely from environment variables
        self.api_key = os.getenv("MYFREESCORENOW_API_KEY", "MOCK_KEY_RJ_BIZ_SOLUTIONS")
        self.client_secret = os.getenv("MYFREESCORENOW_CLIENT_SECRET", "MOCK_SECRET_RJ_BIZ_SOLUTIONS")

    def get_enrollment_url(self, high_value: bool = False) -> str:
        """
        Generates the affiliate enrollment link with the required AID parameter.
        
        @param {bool} high_value - True to use High-Value PID, False for Primary PID.
        @returns {str} Full affiliate landing page URL.
        """
        pid = PID_HIGH_VALUE if high_value else PID_PRIMARY
        return f"https://myfreescorenow.com/enroll/?AID={AFFILIATE_AID}&PID={pid}"

    def register_lead(self, name: str, email: str, phone: str) -> dict:
        """
        Registers a new client lead with MyFreeScoreNow API.
        
        @param {str} name - Client's full name.
        @param {str} email - Client's email address.
        @param {str} phone - Client's phone number.
        @returns {dict} Response from API (contains lead ID or error).
        """
        url = f"{API_BASE_URL}/leads/register"
        payload = {
            "aid": AFFILIATE_AID,
            "first_name": name.split(" ")[0] if " " in name else name,
            "last_name": name.split(" ")[1] if " " in name else "",
            "email": email,
            "phone": phone
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            # If mock key is in place, do a simulated API registration
            if "MOCK_KEY" in self.api_key:
                import uuid
                return {
                    "success": True,
                    "lead_id": f"mfsn_{uuid.uuid4().hex[:12]}",
                    "enrollment_url": self.get_enrollment_url(high_value=False),
                    "message": "Lead registered successfully (RJ Mock Mode)."
                }
                
            res = requests.post(url, json=payload, headers=headers, timeout=30)
            if res.status_code in [200, 201]:
                return res.json()
            return {"success": False, "error": f"HTTP {res.status_code}: {res.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def fetch_credit_report(self, lead_id: str) -> dict:
        """
        Fetches the parsed credit report details for an active lead from the API.
        
        @param {str} lead_id - Verified MyFreeScoreNow Lead ID.
        @returns {dict} Decoded credit report with bureaus details or mock analysis parameters.
        """
        url = f"{API_BASE_URL}/reports/retrieve/{lead_id}"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            if "MOCK_KEY" in self.api_key:
                # Mock high-fidelity data payload to represent typical credit issues for disputing
                return {
                    "success": True,
                    "scores": {"experian": 620, "transunion": 615, "equifax": 610},
                    "negative_items": [
                        {
                            "bureau": "Experian",
                            "item_name": "MIDLAND FUNDING",
                            "account_number": "8572XXXX",
                            "type": "Collection",
                            "reason": "Account is paid, but still shows past due status."
                        },
                        {
                            "bureau": "TransUnion",
                            "item_name": "JPMORGAN CHASE",
                            "account_number": "4826XXXX",
                            "type": "Late Payment",
                            "reason": "30 days late payment reported incorrectly during bank mercy window."
                        },
                        {
                            "bureau": "Equifax",
                            "item_name": "CREDIT ACCEPTANCE CORP",
                            "account_number": "9271XXXX",
                            "type": "Charge Off",
                            "reason": "Discharged in Chapter 7 bankruptcy, must report with $0 balance."
                        }
                    ]
                }
                
            res = requests.get(url, headers=headers, timeout=30)
            if res.status_code == 200:
                return res.json()
            return {"success": False, "error": f"HTTP {res.status_code}: {res.text}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

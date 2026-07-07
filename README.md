<div align="center">
<img src="https://storage.googleapis.com/msgsndr/qQnxRHDtyx0uydPd5sRl/media/67eb83c5e519ed689430646b.jpeg" alt="RJ Business Solutions" width="320"/>

# Credit Repair CRM & Dispute Generator
### Built by **RJ Business Solutions** for **NeuronEdge Labs Inc.** | Architected by **Rick Jefferson**

📍 1342 NM 333, Tijeras, New Mexico 87059 | 🌐 [rickjeffersonsolutions.com](https://rickjeffersonsolutions.com)
</div>

---

## 🚀 Overview

The **Credit Repair CRM & Dispute Generator** is a premium, glassmorphic client portal and back-office tracking tool. Designed specifically for credit restoration businesses, it registers clients, pulls credit report metrics using **MyFreeScoreNow** integration, highlights negative credit items, and constructs print-ready credit dispute letters for Experian, Equifax, and TransUnion.

---

## 📦 Features

- **Client CRM**: Comprehensive tracking of clients, personal details, current credit status, and active scores.
- **MyFreeScoreNow Integration**: Dedicated affiliate enrollment mapping using the mandatory AID (`RickJeffersonSolutions`) and PIDs (`49914` & `30639`).
- **Dispute Letter Builder**: Interactive form to select late payments, inquiries, collections, or charge-offs and compile professional FCRA Section 611-compliant letters.
- **Print Optimization**: Clean style overrides ensuring dispute letters format cleanly when sent to the browser print window for mailing.
- **Email Delivery**: Direct integrations via Resend API to forward dispute templates to clients.

---

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **Database**: SQLite3 (automatic schema provisioning on startup)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Email**: Resend API Integration

---

## ⚙️ Getting Started

### 1. Install Dependencies
Clone the repository and install requirements:
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory and add your keys (see `.env.example`):
```env
MYFREESCORENOW_API_KEY=your_key
RESEND_API_KEY=your_resend_key
```

### 3. Run the Server
Launch the FastAPI development server:
```bash
python main.py
```
Access the client dashboard at: `http://127.0.0.1:8001`

---

## 💼 Corporate & Legal Identity

This project is built on behalf of **NeuronEdge Labs Inc.** and is fully maintained by **RJ Business Solutions**.
- **Owner / Principal**: Rick Jefferson
- **Corporate Entity**: NeuronEdge Labs Inc. (Wyoming C-Corp)
- **Email**: rjbizsolution23@gmail.com
- **Website**: https://rickjeffersonsolutions.com

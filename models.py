# =============================================================================
# Credit Repair CRM & Dispute Generator — Database Layer
# Rick Jefferson | RJ Business Solutions
# 📍 1342 NM 333, Tijeras, New Mexico 87059
# 🌐 https://rickjeffersonsolutions.com
# =============================================================================

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "database.db"

def get_db_connection():
    """Returns a parameterized connection to the local SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables for Client CRM, disputes tracking, and letter histories."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Clients Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT NOT NULL,
        myfreescorenow_id TEXT DEFAULT NULL,
        scores TEXT DEFAULT '{"experian": 0, "transunion": 0, "equifax": 0}',
        status TEXT DEFAULT 'Active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # 2. Disputes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS disputes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        bureau TEXT NOT NULL, -- Experian, TransUnion, Equifax
        item_name TEXT NOT NULL, -- e.g. Midland Funding
        account_number TEXT NOT NULL,
        dispute_reason TEXT NOT NULL,
        status TEXT DEFAULT 'Pending',
        letter_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
    )
    """)
    
    # 3. Generated Letters Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS letters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        bureau TEXT NOT NULL,
        content TEXT NOT NULL,
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
    )
    """)
    
    conn.commit()
    conn.close()
    print(f"[*] Database initialized successfully at: {DB_PATH}")

if __name__ == "__main__":
    init_db()

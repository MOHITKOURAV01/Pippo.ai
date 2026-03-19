import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "audit_logs.db")
def init_db():
    '''Initializes the SQLite database and creates the audits table if it doesn't exist.'''
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                analysis_date TEXT NOT NULL,
                total_clauses INTEGER NOT NULL,
                risky_clauses INTEGER NOT NULL,
                safe_ratio REAL NOT NULL,
                findings_json TEXT NOT NULL
            )
        ''')
        conn.commit()
def save_audit(filename: str, total_clauses: int, risky_clauses: int, safe_ratio: float, findings: List[Dict[str, Any]]) -> int:
    '''Saves a new audit log to the database.'''
    init_db()  
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        current_time = datetime.now().isoformat()
        cursor.execute('''
            INSERT INTO audits (filename, analysis_date, total_clauses, risky_clauses, safe_ratio, findings_json)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (filename, current_time, total_clauses, risky_clauses, safe_ratio, json.dumps(findings)))
        conn.commit()
        return cursor.lastrowid
def get_recent_audits(limit: int = 10) -> List[Dict[str, Any]]:
    '''Retrieves the most recent audit logs.'''
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, filename, analysis_date, total_clauses, risky_clauses, safe_ratio, findings_json 
            FROM audits 
            ORDER BY id DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "filename": row["filename"],
                "analysis_date": row["analysis_date"],
                "total_clauses": row["total_clauses"],
                "risky_clauses": row["risky_clauses"],
                "safe_ratio": row["safe_ratio"],
                "findings": json.loads(row["findings_json"])
            })
        return results

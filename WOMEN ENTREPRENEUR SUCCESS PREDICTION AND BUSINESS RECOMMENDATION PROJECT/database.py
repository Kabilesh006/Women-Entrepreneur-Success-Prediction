import os
import sqlite3
from datetime import datetime
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "submissions.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            investment_inr REAL,
            location TEXT,
            skill TEXT,
            experience TEXT,
            support_network TEXT,
            time_commitment TEXT,
            success_probability REAL,
            prediction_label TEXT,
            recommended_scheme TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_submission(
    investment_inr: float,
    location: str,
    skill: str,
    experience: str,
    support_network: str,
    time_commitment: str,
    success_probability: float,
    prediction_label: str,
    recommended_scheme: str
):
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO submissions (
            timestamp, investment_inr, location, skill, experience,
            support_network, time_commitment, success_probability,
            prediction_label, recommended_scheme
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        now_str, investment_inr, location, skill, experience,
        support_network, time_commitment, success_probability,
        prediction_label, recommended_scheme
    ))
    conn.commit()
    sub_id = cursor.lastrowid
    conn.close()
    return sub_id

def get_all_submissions():
    init_db()
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM submissions ORDER BY id DESC", conn)
    conn.close()
    return df

# Initialize DB on load
init_db()

import sqlite3
from datetime import datetime
from pathlib import Path
import json

class ContextMemory:
    def __init__(self, db_path="out/memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._create_tables()

    def _create_tables(self):
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            dataset_name TEXT,
            total_records INTEGER,
            issues_found INTEGER,
            rules_file TEXT,
            validated_file TEXT
        )
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT,
            decision TEXT,
            confidence REAL,
            dataset TEXT,
            user_comment TEXT,
            timestamp TEXT
        )
        """)
        self.conn.commit()

    def log_session(self, dataset_name, total_records, issues_found, rules_file, validated_file):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO sessions (timestamp, dataset_name, total_records, issues_found, rules_file, validated_file)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), dataset_name, total_records, issues_found, rules_file, validated_file))
        self.conn.commit()

    def log_feedback(self, rule_name, decision, confidence, dataset, user_comment=""):
        cur = self.conn.cursor()
        cur.execute("""
            INSERT INTO feedback (rule_name, decision, confidence, dataset, user_comment, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (rule_name, decision, confidence, dataset, user_comment, datetime.now().isoformat()))
        self.conn.commit()

    def get_feedback_summary(self):
        query = """
        SELECT rule_name, decision, COUNT(*) as count
        FROM feedback
        GROUP BY rule_name, decision
        ORDER BY count DESC
        """
        cur = self.conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()
        return [{"rule_name": r[0], "decision": r[1], "count": r[2]} for r in rows]

    def get_recent_sessions(self, limit=5):
        cur = self.conn.cursor()
        cur.execute("""
            SELECT timestamp, dataset_name, total_records, issues_found, validated_file
            FROM sessions
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))
        rows = cur.fetchall()
        return [
            {
                "timestamp": r[0],
                "dataset": r[1],
                "records": r[2],
                "issues": r[3],
                "validated_file": r[4]
            }
            for r in rows
        ]

    def close(self):
        self.conn.close()

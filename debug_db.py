import sqlite3
import json

def inspect_failed_jobs():
    conn = sqlite3.connect("sora_manager.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, status, error_log FROM jobs WHERE status='failed'")
    rows = cursor.fetchall()
    
    if not rows:
        print("No failed jobs found.")
    else:
        for row in rows:
            jid, status, error_log_json = row
            print(f"Job {jid}: {status}")
            try:
                errors = json.loads(error_log_json)
                for e in errors:
                    print(f" - {e}")
            except:
                print(f" - Raw error: {error_log_json}")

if __name__ == "__main__":
    inspect_failed_jobs()

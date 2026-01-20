import sqlite3
conn = sqlite3.connect('sora_manager.db')

# Reset account status AND QUOTA
conn.execute("UPDATE accounts SET status='AVAILABLE', quota_used_today=0")
conn.commit()
print('Da reset account thanh AVAILABLE + Reset Quota!')

# Xoa het jobs
conn.execute('DELETE FROM jobs')
conn.commit()
print('Da xoa het jobs!')

conn.close()

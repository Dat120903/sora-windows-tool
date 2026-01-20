import sqlite3
conn = sqlite3.connect('sora_manager.db')
conn.execute('DELETE FROM jobs')
conn.commit()
print('DA XOA HET JOBS!')
conn.close()

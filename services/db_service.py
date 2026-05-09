import sqlite3
from datetime import datetime
import subprocess
import re

# ======================
# DATABASE
# ======================
def copy_to_clipboard(text):
    """Copy text to clipboard (Windows)"""
    try:
        # Remove any problematic characters
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)
        process = subprocess.Popen(['powershell', '-Command', f'Set-Clipboard -Value @"\n{text}\n"@'], 
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process.communicate()
        return True
    except Exception as e:
        print(f"Clipboard error: {e}")
        return False

def init_db():
    conn = sqlite3.connect('tiktok_history.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       action_name TEXT, 
                       timestamp TEXT)''')
    conn.commit()
    conn.close()

def save_log(action):
    conn = sqlite3.connect('tiktok_history.db')
    cursor = conn.cursor()
    now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")
    cursor.execute("INSERT INTO logs (action_name, timestamp) VALUES (?, ?)", (action, now))
    conn.commit()
    conn.close()



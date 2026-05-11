import mysql.connector
from datetime import datetime
import subprocess
import re

# ======================
# DATABASE MYSQL (WAMP)
# ======================

def copy_to_clipboard(text):
    """Copy text to clipboard (Windows)"""
    try:
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f]', '', text)

        process = subprocess.Popen(
            ['powershell', '-Command', f'Set-Clipboard -Value @"\n{text}\n"@'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        process.communicate()
        return True

    except Exception as e:
        print(f"Clipboard error: {e}")
        return False


# ======================
# KẾT NỐI MYSQL WAMP
# ======================

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",      # WAMP mặc định thường rỗng
        database="tiktok_db"
    )


# ======================
# TẠO DATABASE + TABLE
# ======================

def init_db():
    # Kết nối trước để tạo database nếu chưa có
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )

    cursor = conn.cursor()

    # Tạo database
    cursor.execute("CREATE DATABASE IF NOT EXISTS tiktok_db")

    conn.close()

    # Kết nối vào database
    conn = connect_db()
    cursor = conn.cursor()

    # Tạo table logs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            action_name VARCHAR(255),
            timestamp VARCHAR(255)
        )
    """)

    conn.commit()
    conn.close()


# ======================
# LƯU LOG
# ======================

def save_log(action):
    conn = connect_db()
    cursor = conn.cursor()

    now = datetime.now().strftime("%H:%M:%S %d/%m/%Y")

    sql = "INSERT INTO logs (action_name, timestamp) VALUES (%s, %s)"
    values = (action, now)

    cursor.execute(sql, values)

    conn.commit()
    conn.close()


# ======================
# TEST
# ======================

init_db()
save_log("Test hành động")
print("Đã lưu log vào MySQL")
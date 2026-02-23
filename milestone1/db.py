import sqlite3
import bcrypt
import datetime
import time

DB_NAME = "users.db"
max_login_attempts = 3
lockout_time = 300  # 5 minutes

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (email TEXT PRIMARY KEY,
                  password BLOB,
                  created_at TEXT)''')

    c.execute('''CREATE TABLE IF NOT EXISTS login_attempts
                 (email TEXT PRIMARY KEY,
                  attempts INTEGER,
                  last_attempt REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS otp_codes
             (email TEXT,
              otp TEXT,
              expiry REAL)''')

    conn.commit()
    conn.close()

def _timestamp():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

# ---------------- REGISTER ----------------

def register_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        c.execute("INSERT INTO users VALUES (?, ?, ?)",
                  (email, hashed, _timestamp()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

# ---------------- LOGIN ----------------

def authenticate_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE email=?", (email,))
    data = c.fetchone()
    conn.close()

    if data:
        if bcrypt.checkpw(password.encode(), data[0]):
            reset_attempts(email)
            return True

    increment_attempts(email)
    return False

# ---------------- RATE LIMIT ----------------

def get_attempts(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT attempts, last_attempt FROM login_attempts WHERE email=?", (email,))
    data = c.fetchone()
    conn.close()
    return data if data else (0, 0)

def increment_attempts(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    attempts, _ = get_attempts(email)
    c.execute("INSERT OR REPLACE INTO login_attempts VALUES (?, ?, ?)",
              (email, attempts + 1, time.time()))
    conn.commit()
    conn.close()

def reset_attempts(email):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM login_attempts WHERE email=?", (email,))
    conn.commit()
    conn.close()

def is_locked(email):
    attempts, last = get_attempts(email)
    if attempts >= max_login_attempts:
        if time.time() - last < lockout_time:
            return True, int(lockout_time - (time.time() - last))
        else:
            reset_attempts(email)
    return False, 0

import random

# ---------------- OTP ----------------

def generate_otp(email):
    otp = str(random.randint(100000, 999999))
    expiry = time.time() + 300  # 5 minutes

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM otp_codes WHERE email=?", (email,))
    c.execute("INSERT INTO otp_codes VALUES (?, ?, ?)",
              (email, otp, expiry))
    conn.commit()
    conn.close()

    return otp

def verify_otp(email, otp_input):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT otp, expiry FROM otp_codes WHERE email=?", (email,))
    data = c.fetchone()
    conn.close()

    if data:
        otp, expiry = data
        if time.time() < expiry and otp == otp_input:
            return True
    return False

def update_password(email, new_password):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(new_password.encode(), salt)
    c.execute("UPDATE users SET password=? WHERE email=?",
              (hashed, email))
    conn.commit()
    conn.close()
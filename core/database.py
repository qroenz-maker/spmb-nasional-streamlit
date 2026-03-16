import sqlite3
import hashlib
import os

DB_PATH = "data/database.db"


def get_connection():
    os.makedirs("data", exist_ok=True)
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # USERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        npsn TEXT
    )
    """)

    # STUDENTS (NIK UNIK NASIONAL)
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        npsn_sekolah_asal TEXT,
        nama_sekolah_asal TEXT,
        nik TEXT UNIQUE,
        nisn TEXT,
        nama TEXT,
        tempat_lahir TEXT,
        tanggal_lahir TEXT,
        jenis_kelamin TEXT,
        nama_ibu_kandung TEXT,
        agama_id TEXT,
        kebutuhan_khusus_id TEXT,
        nomor_kk TEXT,
        npsn_sekolah_tujuan TEXT,
        nama_sekolah_tujuan TEXT,
        uploaded_by TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # KONFLIK
    c.execute("""
    CREATE TABLE IF NOT EXISTS conflicts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        npsn_operator TEXT,
        row_no INTEGER,
        kolom TEXT,
        nilai TEXT,
        alasan TEXT
    )
    """)

    # SESSION
    c.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        username TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # DEFAULT USERS
    c.execute(
        "INSERT OR IGNORE INTO users (username,password,role,npsn) VALUES (?,?,?,?)",
        ("dinas", hash_pw("dinas123"), "DINAS", None)
    )
    c.execute(
        "INSERT OR IGNORE INTO users (username,password,role,npsn) VALUES (?,?,?,?)",
        ("operator1", hash_pw("operator123"), "OPERATOR", "12345678")
    )

    conn.commit()
    conn.close()
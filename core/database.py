import psycopg2
import streamlit as st
import hashlib

# =========================
# CONNECTION
# =========================
def get_connection():
    return psycopg2.connect(
        st.secrets["DATABASE_URL"],
        sslmode="require",
        connect_timeout=10
    )

# =========================
# PASSWORD HASH
# =========================
def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

# =========================
# INIT DATABASE (SAFE)
# =========================
def init_db():
    conn = get_connection()
    c = conn.cursor()

    # USERS
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        npsn TEXT
    )
    """)

    # STUDENTS (NIK UNIK NASIONAL)
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id SERIAL PRIMARY KEY,
        npsn_sekolah_asal TEXT NOT NULL,
        nama_sekolah_asal TEXT NOT NULL,
        nik TEXT UNIQUE NOT NULL,
        nisn TEXT NOT NULL,
        nama TEXT NOT NULL,
        tempat_lahir TEXT NOT NULL,
        tanggal_lahir DATE NOT NULL,
        jenis_kelamin TEXT NOT NULL,
        nama_ibu_kandung TEXT NOT NULL,
        agama_id TEXT,
        kebutuhan_khusus_id TEXT,
        nomor_kk TEXT,
        npsn_sekolah_tujuan TEXT NOT NULL,
        nama_sekolah_tujuan TEXT NOT NULL,
        uploaded_by TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # KONFLIK
    c.execute("""
    CREATE TABLE IF NOT EXISTS conflicts (
        id SERIAL PRIMARY KEY,
        waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        npsn_operator TEXT,
        row_no INTEGER,
        kolom TEXT,
        nilai TEXT,
        alasan TEXT
    )
    """)

    # SESSION LOGIN
    c.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token TEXT PRIMARY KEY,
        username TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # DEFAULT USERS
    c.execute("""
    INSERT INTO users (username, password, role, npsn)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (username) DO NOTHING
    """, ("dinas", hash_pw("dinas123"), "DINAS", None))

    c.execute("""
    INSERT INTO users (username, password, role, npsn)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (username) DO NOTHING
    """, ("operator1", hash_pw("operator123"), "OPERATOR", "12345678"))

    conn.commit()
    conn.close()

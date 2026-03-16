import streamlit as st
import time
import uuid
import hashlib
import extra_streamlit_components as stx

from core.database import init_db, get_connection, hash_pw
from modules.dashboard_page import show_dashboard
from modules.users_page import show_users
from modules.export_dinas_page import show_export_dinas
from modules.upload_page import show_upload
from modules.konflik_page import show_konflik
from modules.monitoring_page import show_monitoring
from modules.template_page import show_template

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="SPMB Nasional",
    page_icon="🎓",
    layout="wide"
)

# =========================
# INIT DATABASE (SAFE – ONCE)
# =========================
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# =========================
# COOKIE MANAGER
# =========================
cookie_manager = stx.CookieManager()

# =========================
# SESSION DEFAULT
# =========================
if "login" not in st.session_state:
    st.session_state.login = False
if "username" not in st.session_state:
    st.session_state.username = None
if "role" not in st.session_state:
    st.session_state.role = None
if "npsn" not in st.session_state:
    st.session_state.npsn = None

# =========================
# AUTO LOGIN VIA COOKIE
# =========================
token = cookie_manager.get("spmb_token")
if token and not st.session_state.login:
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT s.username, u.role, u.npsn
            FROM sessions s
            JOIN users u ON u.username = s.username
            WHERE s.token = %s
            """,
            (token,)
        )
        row = cur.fetchone()
        conn.close()

        if row:
            st.session_state.login = True
            st.session_state.username = row[0]
            st.session_state.role = row[1]
            st.session_state.npsn = row[2]
    except Exception:
        pass

# =========================
# LOGIN PAGE
# =========================
def show_login():
    st.title("🔐 Login SPMB Nasional")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT username, password, role, npsn
            FROM users
            WHERE username = %s
            """,
            (username,)
        )
        user = cur.fetchone()

        if user and user[1] == hash_pw(password):
            token = str(uuid.uuid4())

            cur.execute(
                """
                INSERT INTO sessions (token, username)
                VALUES (%s, %s)
                """,
                (token, username)
            )
            conn.commit()
            conn.close()

            cookie_manager.set(
                "spmb_token",
                token,
                max_age=60 * 60 * 24 * 7  # 7 hari
            )

            st.session_state.login = True
            st.session_state.username = user[0]
            st.session_state.role = user[2]
            st.session_state.npsn = user[3]

            st.success("Login berhasil")
            time.sleep(0.5)
            st.rerun()
        else:
            st.error("Username atau password salah")

# =========================
# LOGOUT
# =========================
def do_logout():
    token = cookie_manager.get("spmb_token")
    if token:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM sessions WHERE token = %s", (token,))
        conn.commit()
        conn.close()

    cookie_manager.delete("spmb_token")
    st.session_state.clear()
    time.sleep(0.2)
    st.rerun()

# =========================
# MAIN APP
# =========================
if not st.session_state.login:
    show_login()
else:
    st.sidebar.title("📋 Menu")

    if st.session_state.role == "DINAS":
        menu = st.sidebar.radio(
            "Menu",
            [
                "Dashboard",
                "Monitoring",
                "Konflik NIK",
                "Manajemen User",
                "Export Dinas",
                "Template"
            ]
        )
    else:  # OPERATOR
        menu = st.sidebar.radio(
            "Menu",
            [
                "Dashboard",
                "Upload Data",
                "Konflik NIK",
                "Template"
            ]
        )

    st.sidebar.divider()
    if st.sidebar.button("Logout"):
        do_logout()

    # =========================
    # ROUTING
    # =========================
    if menu == "Dashboard":
        show_dashboard()

    elif menu == "Upload Data":
        show_upload(st.session_state.npsn)

    elif menu == "Monitoring":
        show_monitoring()

    elif menu == "Konflik NIK":
        show_konflik()

    elif menu == "Manajemen User":
        show_users()

    elif menu == "Export Dinas":
        show_export_dinas()

    elif menu == "Template":
        show_template()

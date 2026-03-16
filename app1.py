import streamlit as st
import hashlib
import sqlite3
import time
import uuid
import extra_streamlit_components as stx

from core.database import init_db
from modules.dashboard_page import show_dashboard
from modules.users_page import show_users
from modules.upload_page import show_upload
from modules.konflik_page import show_konflik
from modules.monitoring_page import show_monitoring
from modules.template_page import show_template


# =========================
# INIT DATABASE
# =========================

init_db()


# =========================
# CONFIG
# =========================

st.set_page_config(
    page_title="SPMB Nasional",
    page_icon="🎓",
    layout="wide"
)


# =========================
# DATABASE
# =========================

DB = "data/database.db"

def get_conn():
    return sqlite3.connect(DB, check_same_thread=False)


# =========================
# COOKIE MANAGER
# =========================

cookie_manager = stx.CookieManager()


# =========================
# SESSION INIT
# =========================

if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.role = None
    st.session_state.npsn = None
    st.session_state.username = None


# =========================
# HASH PASSWORD
# =========================

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


# =========================
# LOGIN FUNCTION
# =========================

def login(username, password):

    conn = get_conn()
    c = conn.cursor()

    c.execute(
        "SELECT role, npsn FROM users WHERE username=? AND password=?",
        (username, hash_pw(password))
    )

    row = c.fetchone()

    if row:
        return row[0], row[1]

    return None, None


# =========================
# AUTO LOGIN FROM TOKEN
# =========================

token = cookie_manager.get("spmb_token")

if token and not st.session_state.login:

    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        SELECT users.username, users.role, users.npsn
        FROM sessions
        JOIN users ON users.username = sessions.username
        WHERE sessions.token=?
    """, (token,))

    row = c.fetchone()

    if row:

        st.session_state.login = True
        st.session_state.username = row[0]
        st.session_state.role = row[1]
        st.session_state.npsn = row[2]


# =========================
# LOGIN PAGE
# =========================

def login_page():

    st.title("🎓 Sistem SPMB Nasional")

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.subheader("Login Sistem")

        with st.form("login_form"):

            username = st.text_input("Username")
            password = st.text_input("Password", type="password")

            submit = st.form_submit_button("Login")

            if submit:

                role, npsn = login(username, password)

                if role is None:

                    st.error("Username atau password salah")

                else:

                    # generate token
                    token = str(uuid.uuid4())

                    conn = get_conn()
                    c = conn.cursor()

                    c.execute(
                        "INSERT INTO sessions (token, username) VALUES (?,?)",
                        (token, username)
                    )

                    conn.commit()

                    cookie_manager.set("spmb_token", token)

                    st.session_state.login = True
                    st.session_state.role = role
                    st.session_state.npsn = npsn
                    st.session_state.username = username

                    st.success("Login berhasil")

                    time.sleep(0.3)

                    st.rerun()


# =========================
# SIDEBAR MENU
# =========================

def sidebar_menu():

    st.sidebar.title("📊 SPMB Nasional")

    st.sidebar.write(f"User : **{st.session_state.username}**")
    st.sidebar.write(f"Role : **{st.session_state.role}**")

    if st.session_state.role == "OPERATOR":
        st.sidebar.write(f"NPSN : **{st.session_state.npsn}**")

    st.sidebar.divider()

    menu_list = [
        "Dashboard",
        "Upload Data",
        "Monitoring",
        "Konflik",
        "Template Excel"
    ]

    # menu khusus dinas
    if st.session_state.role == "DINAS":
        menu_list.append("Manajemen Akun")

    menu = st.sidebar.radio("Menu", menu_list)

    st.sidebar.divider()

    if st.sidebar.button("Logout"):

    # 1. HAPUS SESSION STATE DULU (PALING PENTING)
        st.session_state.login = False
        st.session_state.role = None
        st.session_state.username = None
        st.session_state.npsn = None

    # 2. HAPUS SESSION TOKEN DI DATABASE
        token = cookie_manager.get("spmb_token")
        if token:
            conn = get_conn()
            c = conn.cursor()
            c.execute("DELETE FROM sessions WHERE token=?", (token,))
            conn.commit()
            conn.close()

    # 3. HAPUS COOKIE
        cookie_manager.delete("spmb_token")

    # 4. FORCE RERUN (WAJIB)
        st.rerun()


# =========================
# MAIN APP
# =========================

if not st.session_state.login:

    login_page()

else:

    menu = sidebar_menu()

    if menu == "Dashboard":

        show_dashboard()

    elif menu == "Upload Data":

        if st.session_state.role == "OPERATOR":
            show_upload(st.session_state.npsn)
        else:
            st.warning("Menu ini hanya untuk operator sekolah")

    elif menu == "Monitoring":

        if st.session_state.role == "DINAS":
            show_monitoring()
        else:
            st.warning("Menu ini hanya untuk dinas")

    elif menu == "Konflik":

        show_konflik()

    elif menu == "Template Excel":

        show_template()

    elif menu == "Manajemen Akun":

        if st.session_state.role == "DINAS":
            show_users()
        else:
            st.warning("Menu ini hanya untuk dinas")
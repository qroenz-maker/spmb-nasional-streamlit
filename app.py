import streamlit as st
import hashlib
import time
import uuid
import extra_streamlit_components as stx

from core.database import init_db
from modules.dashboard_page import show_dashboard
from modules.users_page import show_users
from modules.export_dinas_page import show_export_dinas
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
    st.session_state.username = None
    st.session_state.npsn = None

# =========================
# HASH PASSWORD
# =========================
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# =========================
# HANDLE LOGOUT FLAG
# =========================
if st.session_state.get("logout"):
    st.session_state.clear()
    st.session_state.login = False

# =========================
# AUTO LOGIN FROM COOKIE
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
    conn.close()

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

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.subheader("Login Sistem")

        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")

            if submit:

                conn = get_conn()
                c = conn.cursor()

                c.execute(
                    "SELECT role,npsn FROM users WHERE username=? AND password=?",
                    (username, hash_pw(password))
                )

                row = c.fetchone()
                conn.close()

                if not row:
                    st.error("Username atau password salah")
                else:
                    token = str(uuid.uuid4())

                    conn = get_conn()
                    c = conn.cursor()
                    c.execute(
                        "INSERT INTO sessions (token,username) VALUES (?,?)",
                        (token, username)
                    )
                    conn.commit()
                    conn.close()

                    cookie_manager.set("spmb_token", token)

                    st.session_state.login = True
                    st.session_state.username = username
                    st.session_state.role = row[0]
                    st.session_state.npsn = row[1]

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
        "Export Nasional",
        "Konflik",
        "Template Excel"
    ]

    if st.session_state.role == "DINAS":
        menu_list.append("Manajemen Akun")

    menu = st.sidebar.radio("Menu", menu_list)

    st.sidebar.divider()

    if st.sidebar.button("Logout"):

        token = cookie_manager.get("spmb_token")
        if token:
            conn = get_conn()
            c = conn.cursor()
            c.execute("DELETE FROM sessions WHERE token=?", (token,))
            conn.commit()
            conn.close()

        cookie_manager.delete("spmb_token")

        st.session_state.logout = True
        st.rerun()

    return menu

# =========================
# MAIN APP FLOW (KUNCI STABIL)
# =========================
if not st.session_state.login:
    login_page()
    st.stop()   # ⛔ PENTING: HENTIKAN RENDER

menu = sidebar_menu()

if menu == "Dashboard":
    show_dashboard()

elif menu == "Upload Data":
    if st.session_state.role == "OPERATOR":
        show_upload(st.session_state.npsn)
    else:
        st.warning("Menu ini hanya untuk operator sekolah")

elif menu == "Export Nasional":
    if st.session_state.role == "DINAS":
        show_export_dinas()
    else:
        st.warning("Menu ini hanya untuk dinas")

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

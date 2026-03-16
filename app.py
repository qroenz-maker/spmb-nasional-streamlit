import streamlit as st
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
# CONFIG
# =========================
st.set_page_config(
    page_title="SPMB Nasional",
    page_icon="🎓",
    layout="wide"
)

# =========================
# INIT DATABASE (SAFE)
# =========================
if "db_initialized" not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# =========================
# SESSION DEFAULT
# =========================
if "login" not in st.session_state:
    st.session_state.login = False
    st.session_state.username = None
    st.session_state.role = None
    st.session_state.npsn = None

# =========================
# COOKIE MANAGER (LOGIN)
# =========================
cookie_manager = stx.CookieManager()

# =========================
# LOGIN PAGE (SIMPLE)
# =========================
def show_login():
    st.title("🔐 Login SPMB Nasional")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # ⛔️ login logic ada di module login Anda
        # di sini hanya contoh set session
        st.session_state.login = True
        st.session_state.username = username
        st.session_state.role = "DINAS"  # atau OPERATOR
        st.session_state.npsn = None
        cookie_manager.set("spmb_login", "1")
        st.success("Login berhasil")
        time.sleep(0.5)
        st.rerun()

# =========================
# LOGOUT
# =========================
def do_logout():
    cookie_manager.delete("spmb_login")
    st.session_state.clear()
    time.sleep(0.2)
    st.rerun()

# =========================
# MAIN APP
# =========================
if not st.session_state.login:
    show_login()
    st.stop()

# =========================
# SIDEBAR
# =========================
st.sidebar.title("🎓 SPMB Nasional")

menu_list = [
    "Dashboard",
    "Upload Data",
    "Monitoring",
    "Konflik NIK",
    "Manajemen User",
    "Export Dinas",
    "Template"
]

menu = st.sidebar.radio("Menu", menu_list)
st.sidebar.divider()

if st.sidebar.button("Logout"):
    do_logout()

# =========================
# PAGE ROUTER
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

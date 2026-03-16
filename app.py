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

# =========================
# SIDEBAR / MENU (contoh)
# =========================
if st.session_state.login:
    menu = st.sidebar.radio(
        "Menu",
        [
            "Dashboard",
            "Upload Data",
            "Monitoring",
            "Konflik NIK",
            "Manajemen User",
            "Export Dinas",
            "Template"
        ]
    )

    if menu == "Dashboard":
        show_dashboard()
    elif menu == "Upload Data":
        show_upload(st.session_state.get("npsn"))
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

else:
    st.info("Silakan login terlebih dahulu")

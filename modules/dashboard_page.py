import streamlit as st
import pandas as pd
from core.database import get_connection


def show_dashboard():

    st.title("📊 Dashboard SPMB Nasional")

    conn = get_connection()

    # =========================
    # DATA SISWA
    # =========================
    df_students = pd.read_sql(
        "SELECT * FROM students",
        conn
    )

    total = len(df_students)

    st.metric("Total Data Siswa", total)

    # =========================
    # PER SEKOLAH TUJUAN
    # =========================
    if not df_students.empty:
        per_sekolah = (
            df_students
            .groupby("npsn_sekolah_tujuan")
            .size()
            .reset_index(name="jumlah")
        )

        st.subheader("Jumlah Pendaftar per Sekolah Tujuan")
        st.dataframe(per_sekolah, use_container_width=True)

    # =========================
    # DATA KONFLIK
    # =========================
    df_conflict = pd.read_sql(
        "SELECT * FROM conflicts",
        conn
    )

    st.metric("Total Konflik NIK", len(df_conflict))

    conn.close()
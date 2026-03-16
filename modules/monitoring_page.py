import streamlit as st
import pandas as pd
from core.database import get_connection


def show_monitoring():

    st.title("📈 Monitoring SPMB Nasional")

    conn = get_connection()

    # =========================
    # REKAP PER SEKOLAH TUJUAN
    # =========================
    df = pd.read_sql(
        """
        SELECT
            npsn_sekolah_tujuan,
            nama_sekolah_tujuan,
            COUNT(*) AS jumlah
        FROM students
        GROUP BY npsn_sekolah_tujuan, nama_sekolah_tujuan
        ORDER BY jumlah DESC
        """,
        conn
    )

    if df.empty:
        st.info("Belum ada data pendaftar")
        conn.close()
        return

    st.subheader("Jumlah Pendaftar per Sekolah Tujuan")
    st.dataframe(df, use_container_width=True)

    # =========================
    # TOTAL NASIONAL
    # =========================
    total = df["jumlah"].sum()
    st.metric("Total Pendaftar Nasional", int(total))

    conn.close()
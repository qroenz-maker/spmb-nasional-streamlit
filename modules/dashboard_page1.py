import streamlit as st
import pandas as pd
from core.database import get_connection

def show_dashboard():

    st.title("📊 Dashboard SPMB Nasional")

    conn = get_connection()

    # =========================
    # DATA UTAMA
    # =========================

    df_students = pd.read_sql("SELECT * FROM students", conn)
    df_conflict = pd.read_sql("SELECT * FROM conflicts", conn)

    total_siswa = len(df_students)
    total_konflik = len(df_conflict)

    if "npsn_tujuan" in df_students.columns:
        sekolah_upload = df_students["npsn_tujuan"].nunique()
    else:
        sekolah_upload = 0

    # =========================
    # METRIC BOX
    # =========================

    col1, col2, col3 = st.columns(3)

    col1.metric(
        label="Total Data Siswa",
        value=f"{total_siswa:,}"
    )

    col2.metric(
        label="Total Konflik",
        value=f"{total_konflik:,}"
    )

    col3.metric(
        label="Sekolah Sudah Upload",
        value=f"{sekolah_upload:,}"
    )

    st.divider()

    # =========================
    # GRAFIK DATA PER SEKOLAH
    # =========================

    st.subheader("📊 Jumlah Siswa per Sekolah")

    if total_siswa > 0:

        df_chart = (
            df_students
            .groupby("npsn_tujuan")
            .size()
            .reset_index(name="jumlah")
            .sort_values("jumlah", ascending=False)
        )

        st.bar_chart(
            df_chart.set_index("npsn_tujuan")
        )

    else:
        st.info("Belum ada data upload")

    st.divider()

    # =========================
    # GRAFIK KONFLIK
    # =========================

    st.subheader("⚠ Konflik Data per Sekolah")

    if total_konflik > 0:

        df_konflik_chart = (
            df_conflict
            .groupby("npsn_operator")
            .size()
            .reset_index(name="jumlah")
        )

        st.bar_chart(
            df_konflik_chart.set_index("npsn_operator")
        )

    else:
        st.success("Tidak ada konflik data")

    st.divider()

    # =========================
    # TABEL DATA TERBARU
    # =========================

    st.subheader("📋 Data Upload Terbaru")

    if total_siswa > 0:

        df_latest = df_students.tail(50)

        st.dataframe(
            df_latest,
            use_container_width=True
        )

    else:
        st.info("Belum ada data")
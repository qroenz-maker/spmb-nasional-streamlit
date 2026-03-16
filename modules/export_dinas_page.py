import streamlit as st
import pandas as pd
from core.database import get_connection


def show_export_dinas():

    st.title("⬇️ Export Data SPMB Nasional (CSV Resmi)")

    # =====================================================
    # HEADER TEMPLATE NASIONAL (WAJIB & BAKU)
    # =====================================================
    columns = [
        "npsn_sekolah_asal",
        "nama_sekolah_asal",
        "nik",
        "nisn",
        "nama",
        "tempat_lahir",
        "tanggal_lahir",
        "jenis_kelamin",
        "nama_ibu_kandung",
        "agama_id",
        "kebutuhan_khusus_id",
        "nomor_kk",
        "npsn_sekolah_tujuan",
        "nama_sekolah_tujuan"
    ]

    conn = get_connection()

    df = pd.read_sql(
        f"""
        SELECT {",".join(columns)}
        FROM students
        ORDER BY npsn_sekolah_tujuan, nama
        """,
        conn
    )

    conn.close()

    if df.empty:
        st.info("Belum ada data siswa nasional")
        return

    # =====================================================
    # NORMALISASI WAJIB SESUAI ATURAN NASIONAL
    # =====================================================

    # Semua kolom jadi STRING (AMAN CSV & SQL)
    for col in columns:
        if col != "tanggal_lahir":
            df[col] = df[col].astype(str).fillna("").str.strip()

    # tanggal_lahir:
    # - Format baku: yyyy-mm-dd
    # - Dipaksa TEXT agar Excel tidak mengubah
    df["tanggal_lahir"] = (
        pd.to_datetime(df["tanggal_lahir"], errors="coerce")
        .dt.strftime("%Y-%m-%d")
        .apply(lambda x: f"'{x}" if pd.notna(x) else "")
    )

    st.success(f"Total Data Nasional: {len(df)}")
    st.dataframe(df, use_container_width=True)

    # =====================================================
    # EXPORT CSV RESMI NASIONAL
    # =====================================================
    csv_data = df.to_csv(
        index=False,
        encoding="utf-8"
    )

    st.download_button(
        "⬇️ Download CSV Nasional (Format Resmi)",
        data=csv_data,
        file_name="spmb_nasional.csv",
        mime="text/csv"
    )
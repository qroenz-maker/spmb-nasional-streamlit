import streamlit as st
import pandas as pd

from core.database import get_connection
from modules.validation_engine import validate_dataframe, detect_nik_conflict


def show_upload(npsn_operator):
    st.title("📤 Upload Data SPMB Nasional")

    file = st.file_uploader(
        "Upload Excel Template Nasional",
        type=["xlsx"]
    )

    if not file:
        return

    # ============================
    # READ EXCEL
    # ============================
    try:
        df = pd.read_excel(file, sheet_name="template_upload")
    except Exception:
        st.error("Sheet harus bernama: template_upload")
        return

    # ============================
    # VALIDASI TEMPLATE & ISI
    # ============================
    errors = validate_dataframe(df)
    if errors:
        st.error("Data tidak valid")
        for e in errors[:20]:
            st.write("•", e)
        st.stop()

    # ============================
    # NORMALISASI NPSN (KRUSIAL)
    # ============================
    df["npsn_sekolah_tujuan"] = (
        df["npsn_sekolah_tujuan"]
        .astype(str)
        .str.replace(".0", "", regex=False)
        .str.strip()
    )

    npsn_operator = str(npsn_operator).strip()

    # ============================
    # FILTER SESUAI OPERATOR
    # ============================
    df_operator = df[df["npsn_sekolah_tujuan"] == npsn_operator]

    if df_operator.empty:
        st.error(
            "Tidak ada data yang sesuai dengan NPSN akun operator.\n\n"
            f"NPSN Operator : {npsn_operator}\n"
            f"NPSN di File  : {df['npsn_sekolah_tujuan'].unique().tolist()}"
        )
        st.stop()

    # ============================
    # CEK KONFLIK NIK NASIONAL
    # ============================
    conn = get_connection()
    konflik = detect_nik_conflict(df_operator, conn)

    if not konflik.empty:
        st.warning("Ditemukan konflik NIK nasional")

        for _, r in konflik.iterrows():
            conn.execute(
                """
                INSERT INTO conflicts
                (npsn_operator, row_no, kolom, nilai, alasan)
                VALUES (?,?,?,?,?)
                """,
                (
                    npsn_operator,
                    r["row"],
                    "nik",
                    r["nik"],
                    f"NIK sudah terdaftar di sekolah {r['sekolah_terdaftar']}"
                )
            )

        conn.commit()
        st.dataframe(konflik, use_container_width=True)
        st.stop()

    # ============================
    # INSERT DATA VALID
    # ============================
    df_operator = df_operator.copy()
    df_operator["uploaded_by"] = st.session_state.username

    df_operator.to_sql(
        "students",
        conn,
        if_exists="append",
        index=False
    )

    conn.close()

    st.success(f"Upload berhasil: {len(df_operator)} data")
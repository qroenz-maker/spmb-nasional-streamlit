import streamlit as st
import hashlib
import pandas as pd
import io
import psycopg2
from psycopg2 import sql, extras

DB_URL = st.secrets["DATABASE_URL"]
DEFAULT_PASSWORD = "123456"

# ===============================
# DATABASE
# ===============================
def get_conn():
    return psycopg2.connect(
        DB_URL,
        sslmode="require",
        connect_timeout=10
    )

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ===============================
# PAGE
# ===============================
def show_users():
    st.title("👥 Manajemen Akun Operator Sekolah")

    tab1, tab2, tab3, tab4 = st.tabs([
        "Download Template",
        "Import Operator",
        "Reset Password",
        "Export Operator"
    ])

    # =====================================================
    # TAB 1 DOWNLOAD TEMPLATE
    # =====================================================
    with tab1:
        st.subheader("Download Template Import Operator")
        template = pd.DataFrame({
            "username": ["operator_1001"],
            "npsn": ["10010001"]
        })
        buffer = io.BytesIO()
        template.to_excel(buffer, index=False)
        st.download_button(
            "⬇ Download Template Excel",
            buffer.getvalue(),
            file_name="template_operator.xlsx"
        )
        st.info(
            "Ketentuan:\n"
            "- 1 NPSN hanya boleh memiliki 1 operator\n"
            "- Password default operator adalah: 123456"
        )

    # =====================================================
    # TAB 2 IMPORT OPERATOR
    # =====================================================
    with tab2:
        st.subheader("Import Akun Operator dari Excel")
        file = st.file_uploader("Upload Excel Operator", type=["xlsx"])
        if file:
            df = pd.read_excel(file)
            required = ["username", "npsn"]
            if not all(col in df.columns for col in required):
                st.error("Format Excel tidak sesuai template")
                st.stop()

            conn = get_conn()
            c = conn.cursor()

            success = 0
            duplicate_npsn = 0
            skipped = 0
            result_data = []

            for _, row in df.iterrows():
                username = str(row["username"]).strip()
                npsn = str(row["npsn"]).strip()
                if not username or not npsn:
                    skipped += 1
                    continue

                # CEK NPSN SUDAH ADA ATAU BELUM
                c.execute(
                    "SELECT 1 FROM users WHERE role='OPERATOR' AND npsn=%s",
                    (npsn,)
                )
                if c.fetchone():
                    duplicate_npsn += 1
                    continue

                try:
                    c.execute(
                        """INSERT INTO users (username, password, role, npsn)
                           VALUES (%s, %s, %s, %s)""",
                        (username, hash_pw(DEFAULT_PASSWORD), "OPERATOR", npsn)
                    )
                    result_data.append({"username": username, "npsn": npsn})
                    success += 1
                except psycopg2.IntegrityError:
                    skipped += 1

            conn.commit()
            conn.close()

            st.success(f"{success} akun operator berhasil dibuat")
            if duplicate_npsn > 0:
                st.warning(f"{duplicate_npsn} NPSN sudah memiliki operator (dilewati)")
            if skipped > 0:
                st.info(f"{skipped} baris dilewati karena tidak valid / error")
            if success > 0:
                st.info("Password default semua operator: 123456")

            df_out = pd.DataFrame(result_data)
            buffer = io.BytesIO()
            df_out.to_excel(buffer, index=False)
            st.download_button(
                "⬇ Download Daftar Akun Operator Baru",
                buffer.getvalue(),
                file_name="akun_operator_baru.xlsx"
            )

    # =====================================================
    # TAB 3 RESET PASSWORD
    # =====================================================
    with tab3:
        st.subheader("Reset Password Operator")
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT username, npsn FROM users WHERE role='OPERATOR' ORDER BY npsn"
        )
        users = c.fetchall()
        conn.close()

        if not users:
            st.warning("Belum ada akun operator")
            return

        user_list = [f"{u[1]} - {u[0]}" for u in users]
        selected = st.selectbox("Pilih Operator (NPSN - Username)", user_list)

        new_pw = st.text_input("Password Baru", type="password")

        if st.button("Reset Password"):
            if not new_pw:
                st.error("Password tidak boleh kosong")
                st.stop()
            npsn = selected.split(" - ")[0]

            conn = get_conn()
            c = conn.cursor()
            c.execute(
                "UPDATE users SET password=%s WHERE role='OPERATOR' AND npsn=%s",
                (hash_pw(new_pw), npsn)
            )
            conn.commit()
            conn.close()
            st.success("Password operator berhasil direset")

    # =====================================================
    # TAB 4 EXPORT OPERATOR
    # =====================================================
    with tab4:
        st.subheader("Export Daftar Operator Sekolah")
        conn = get_conn()
        df = pd.read_sql_query(
            "SELECT npsn, username FROM users WHERE role='OPERATOR' ORDER BY npsn",
            conn
        )
        conn.close()

        st.dataframe(df, use_container_width=True)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        st.download_button(
            "⬇ Download Excel Operator",
            buffer.getvalue(),
            file_name="daftar_operator.xlsx"
        )

    # =====================================================
    # STATISTIK
    # =====================================================
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users WHERE role='OPERATOR'")
    total = c.fetchone()[0]
    conn.close()
    st.metric("Total Operator Sekolah", total)

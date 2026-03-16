import streamlit as st
import pandas as pd
import io

def show_template():

    st.title("📄 Template Upload Data SPMB")

# =========================
# HEADER TEMPLATE
# =========================

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

# =========================
# CONTOH DATA
# =========================

    data = [[
        "00000000",
        "belum sekolah",
        "1871102909060004",
        "0055465018",
        "Nurhaeni",
        "Jakarta",
        "2007-05-06",
        "p",
        "Turiyah",
        "1",
        "0",
        "3404104304180002",
        "25802400",
        "tk aisiyah"
    ]]

    df = pd.DataFrame(data, columns=columns)

# =========================
# SHEET AGAMA
# =========================

    agama = pd.DataFrame({
        "agama_id":[1,2,3,4,5,6,7,99],
        "nama":[
            "Islam",
            "Kristen",
            "Katholik",
            "Hindu",
            "Budha",
            "Khonghucu",
            "Kepercayaan kpd Tuhan YME",
            "Lainnya"
        ]
    })

# =========================
# SHEET KEBUTUHAN KHUSUS
# =========================

    kebutuhan = pd.DataFrame({
        "kebutuhan_khusus_id":[
            0,1,2,4,8,16,32,64,128,256,
            512,1024,2048,4096,8192,16384,32768
        ],
        "nama":[
            "Tidak ada",
            "A - Tuna netra",
            "B - Tuna rungu",
            "C - Tuna grahita ringan",
            "C1 - Tuna grahita sedang",
            "D - Tuna daksa ringan",
            "D1 - Tuna daksa sedang",
            "E - Tuna laras",
            "F - Tuna wicara",
            "H - Hiperaktif",
            "I - Cerdas istimewa",
            "J - Bakat istimewa",
            "K - Kesulitan belajar",
            "N - Narkoba",
            "O - Indigo",
            "P - Down syndrome",
            "Q - Autis"
        ]
    })

# =========================
# EXPORT EXCEL
# =========================

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:

        df.to_excel(writer, sheet_name="template_upload", index=False)
        agama.to_excel(writer, sheet_name="referensi_agama", index=False)
        kebutuhan.to_excel(writer, sheet_name="referensi_kebutuhan_khusus", index=False)

    st.download_button(
        label="⬇ Download Template Excel SPMB",
        data=buffer.getvalue(),
        file_name="template_upload_spmb.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.info("Gunakan template ini untuk upload data siswa SPMB.")
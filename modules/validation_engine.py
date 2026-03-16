import re
import pandas as pd

REQUIRED_COLUMNS = [
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


def validate_dataframe(df: pd.DataFrame):
    errors = []

    if list(df.columns) != REQUIRED_COLUMNS:
        errors.append("Header tidak sesuai template nasional")
        return errors

    for i, row in df.iterrows():
        nik = str(row["nik"])
        if not re.fullmatch(r"\d{16}", nik):
            errors.append(f"Baris {i+2}: NIK tidak valid")

        jk = str(row["jenis_kelamin"]).upper()
        if jk not in ["L", "P"]:
            errors.append(f"Baris {i+2}: Jenis kelamin harus L/P")

    return errors


def detect_nik_conflict(df, conn):
    conflicts = []
    cur = conn.cursor()

    for i, nik in enumerate(df["nik"]):
        cur.execute("SELECT npsn_sekolah_tujuan FROM students WHERE nik=?", (str(nik),))
        row = cur.fetchone()
        if row:
            conflicts.append({
                "row": i + 2,
                "nik": nik,
                "sekolah_terdaftar": row[0]
            })

    return pd.DataFrame(conflicts)
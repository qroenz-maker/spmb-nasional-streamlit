def detect_nik_conflict(df, conn):
    conflicts = []
    cur = conn.cursor()

    for i, nik in enumerate(df["nik"]):
        cur.execute(
            "SELECT npsn_sekolah_tujuan FROM students WHERE nik=%s",
            (str(nik),)
        )
        row = cur.fetchone()
        if row:
            conflicts.append({
                "row": i + 2,
                "nik": nik,
                "sekolah_terdaftar": row[0]
            })

    cur.close()
    return pd.DataFrame(conflicts)

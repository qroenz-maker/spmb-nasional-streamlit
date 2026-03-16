from core.database import get_connection

def bulk_insert(data):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO spmb (nik,nama,npsn_asal,npsn_tujuan) VALUES (?,?,?,?)",
        data
    )

    conn.commit()
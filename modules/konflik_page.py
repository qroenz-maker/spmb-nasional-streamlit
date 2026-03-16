import streamlit as st
import pandas as pd
from core.database import get_connection


def show_konflik():

    st.title("⚠ Data Konflik SPMB")

    conn = get_connection()

    df = pd.read_sql("SELECT * FROM conflicts", conn)

    if df.empty:

        st.success("Tidak ada konflik data")

        return

    st.write("Total konflik:", len(df))

    st.dataframe(
        df,
        use_container_width=True
    )

    st.download_button(
        "Download Konflik CSV",
        df.to_csv(index=False),
        "konflik_spmb.csv"
    )
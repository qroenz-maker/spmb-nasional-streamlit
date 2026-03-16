import streamlit as st

def progress_bar(total):

    bar=st.progress(0)

    def update(i):

        percent=int((i/total)*100)

        bar.progress(percent)

    return update
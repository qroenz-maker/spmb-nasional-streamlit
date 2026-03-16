def clean_dataframe(df):

    df.columns=df.columns.str.strip()

    df["NIK"]=df["NIK"].astype(str).str.strip()

    df["NAMA"]=df["NAMA"].str.strip()

    df=df.dropna(subset=["NIK"])

    df=df.drop_duplicates(subset=["NIK"])

    return df
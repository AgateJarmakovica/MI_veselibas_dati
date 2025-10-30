import streamlit as st, pandas as pd, json
from ..pipeline import run_pipeline

st.set_page_config(page_title="healthdq-ai", layout="wide")
st.title("healthdq-ai — Precizitāte • Pilnīgums • Atkārtota izmantojamība")

cfg = "configs/rules.yml"
kind = st.selectbox("Ievades formāts", ["csv","json","fhir"])

default_path = "data/sample/500_dati_testiem.csv" if kind=="csv" else ""
path = st.text_input("Datu ceļš", value=default_path)
out_dir = st.text_input("Izvades mape", value="out")

if st.button("Palaist"):
    try:
        df, issues, metrics = run_pipeline(path, kind, cfg, out_dir)
        t1, t2, t3 = st.tabs(["Tīrītie dati","Problēmas (Precision)","Metrikas (Pirms/Pēc)"])
        with t1:
            st.dataframe(df, use_container_width=True)
            st.download_button("Lejupielādēt cleaned.csv", data=df.to_csv(index=False), file_name="cleaned.csv")
        with t2:
            st.dataframe(issues, use_container_width=True, height=300)
        with t3:
            st.json(metrics)
    except Exception as e:
        st.error(str(e))

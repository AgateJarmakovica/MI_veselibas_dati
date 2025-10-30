"""
healthdq.ui — Lietotāja interfeiss veselības datu kvalitātes prototipam
=======================================================================

Šis modulis nodrošina interaktīvu lietotāja saskarni, kas ļauj
palaist un vizualizēt *healthdq-ai* datu kvalitātes novērtēšanas cauruļvadu (pipeline).
Tas ir izstrādāts kā daļa no promocijas darba
“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai
atvērtās zinātnes iniciatīvās”.

Mērķis:
--------
Nodrošināt cilvēkam saprotamu un reproducējamu vizualizācijas vidi,
kurā lietotājs var:
- augšupielādēt veselības datus (CSV, JSON, FHIR),
- palaist datu kvalitātes noteikumu dzinēju un transformācijas (Precision, Completeness, Reusability),
- apskatīt un lejupielādēt uzlabotos (cleaned) datus,
- salīdzināt datu kvalitātes metriku pirms un pēc apstrādes.

Atbilst **FAIR datu principiem** — reproducējamība, pārskatāmība un atkārtota izmantojamība.

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

import streamlit as st
import pandas as pd
import json
from ..pipeline import run_pipeline
import datetime

# ---------------------------------------------------------------------
# LAPAS KONFIGURĀCIJA
# ---------------------------------------------------------------------
st.set_page_config(page_title="healthdq-ai", layout="wide", page_icon="🩺")

st.title("🧠 healthdq-ai — Datu kvalitātes uzlabošana veselības aprūpē")
st.caption("Precizitāte • Pilnīgums • Atkārtota izmantojamība — FAIR & DCAI pieeja")

# ---------------------------------------------------------------------
# LIETOTĀJA IEVADES KONFIGURĀCIJA
# ---------------------------------------------------------------------
cfg = st.text_input("🧩 Noteikumu konfigurācijas fails (YAML)", value="configs/rules.yml")
kind = st.selectbox("📦 Ievades datu formāts", ["csv", "json", "fhir"])

default_path = "data/sample/500_dati_testiem.csv" if kind == "csv" else ""
path = st.text_input("📁 Datu fails", value=default_path)
out_dir = st.text_input("📤 Izvades mape", value="out")

st.markdown("---")

# ---------------------------------------------------------------------
# POGA: PALAIST PIPELINE
# ---------------------------------------------------------------------
if st.button("🚀 Palaist datu kvalitātes novērtēšanu"):
    start_time = datetime.datetime.now()
    st.info("⏳ Analizēju datus, lūdzu, uzgaidiet...")

    try:
        df, issues, metrics = run_pipeline(path, kind, cfg, out_dir)
        duration = (datetime.datetime.now() - start_time).total_seconds()

        st.success(f"✅ Datu kvalitātes analīze pabeigta {duration:.2f} sekundēs.")

        # -----------------------------------------------------------------
        # REZULTĀTU SKATI
        # -----------------------------------------------------------------
        t1, t2, t3, t4 = st.tabs([
            "🧹 Tīrītie dati",
            "⚠️ Problēmas (Precision)",
            "📊 Metrikas (Pirms/Pēc)",
            "🧾 Sesijas informācija"
        ])

        # ---------------------- TAB 1 ----------------------
        with t1:
            st.subheader("Tīrītie (uzlabotie) dati")
            st.dataframe(df, use_container_width=True)
            st.download_button(
                "💾 Lejupielādēt cleaned.csv",
                data=df.to_csv(index=False),
                file_name="cleaned.csv",
                mime="text/csv"
            )

        # ---------------------- TAB 2 ----------------------
        with t2:
            st.subheader("Datu kvalitātes pārkāpumi (Precision)")
            if len(issues) == 0:
                st.success("Nav atrastu pārkāpumu 🎉")
            else:
                st.dataframe(issues, use_container_width=True, height=400)

        # ---------------------- TAB 3 ----------------------
        with t3:
            st.subheader("Metrikas pirms un pēc AI apstrādes")
            st.json(metrics, expanded=False)

        # ---------------------- TAB 4 ----------------------
        with t4:
            st.subheader("Reproducējamības metadati")
            meta = {
                "timestamp": datetime.datetime.now().isoformat(),
                "input_path": path,
                "rules_config": cfg,
                "output_dir": out_dir,
                "format": kind,
                "records_processed": len(df),
                "issues_detected": len(issues),
            }
            st.json(meta)

    except FileNotFoundError:
        st.error("❌ Norādītais datu fails vai konfigurācija nav atrasta.")
    except Exception as e:
        st.error(f"❌ Kļūda izpildē: {e}")

# ---------------------------------------------------------------------
# LAPAS ZEMTEKSTS
# ---------------------------------------------------------------------
st.markdown("---")
st.caption("© 2025 Agate Jarmakoviča | healthdq-ai | Data-Centric AI for FAIR Healthcare Data")

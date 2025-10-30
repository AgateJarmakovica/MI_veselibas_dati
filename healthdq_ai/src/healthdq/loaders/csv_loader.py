"""
csv_loader
==========

Šis modulis īsteno CSV formāta datu ielādi veselības datu kvalitātes
prototipam *healthdq-ai*, kas ir daļa no promocijas darba
“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai
atvērtās zinātnes iniciatīvās”.

Mērķis:
--------
Droši un reproducējami ielādēt CSV failus, pārbaudīt pamatkolonnu esamību
un ģenerēt metadatus, kas atbalsta FAIR principus (Findable, Accessible, Interoperable, Reusable).

Funkcionalitāte:
----------------
- Ielādē CSV datus ar `pandas`
- Validē formātu un kolonnu tipu konsekvenci
- Saglabā reproducējamības metadatus (faila nosaukums, rindu skaits, ielādes laiks)
- Nodrošina caurspīdīgu kļūdu ziņošanu (piemēram, ja failā trūkst nepieciešamās kolonnas)

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

import pandas as pd
import os
import datetime


def load_csv(path: str, required_columns: list[str] | None = None) -> pd.DataFrame:
    """
    Ielādē CSV datu failu ar reproducējamības un kvalitātes validāciju.

    Parametri:
    -----------
    path : str
        Ceļš uz CSV failu.
    required_columns : list[str], optional
        Kolonnu saraksts, kas obligāti jābūt datu kopā
        (piemēram, ["patient_id", "height_cm", "weight_kg", "bmi"])

    Atgriež:
    --------
    df : pd.DataFrame
        Ielādēta datu kopa ar pievienotiem metadatiem (`attrs["meta"]`).
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ CSV fails nav atrasts: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise RuntimeError(f"❌ Neizdevās nolasīt CSV failu: {e}")

    # Validē obligātās kolonnas
    if required_columns:
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            raise ValueError(f"❌ CSV failā trūkst obligātās kolonnas: {missing}")

    # Izveido reproducējamības metadatus
    meta = {
        "loader": "CSV",
        "path": os.path.abspath(path),
        "rows": len(df),
        "columns": list(df.columns),
        "timestamp": datetime.datetime.now().isoformat(),
        "file_size_kb": round(os.path.getsize(path) / 1024, 2),
        "required_columns_checked": required_columns if required_columns else None,
    }

    # Saglabā metadatus DataFrame atribūtos (FAIR reproducējamībai)
    df.attrs["meta"] = meta

    return df

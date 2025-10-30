"""
json_loader
===========

Šis modulis īsteno JSON formāta datu ielādi veselības datu kvalitātes prototipam
*healthdq-ai*, kas ir daļa no promocijas darba
“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai
atvērtās zinātnes iniciatīvās”.

Mērķis:
--------
Droši, pārredzami un reproducējami ielādēt JSON ierakstus (no failiem vai API),
pārveidojot tos uz strukturētu pandas DataFrame formātu tālākai datu kvalitātes analīzei.

Funkcionalitāte:
----------------
- Ielādē JSON failus (ierakstu sarakstus vai atsevišķus vārdnīcu objektus)
- Nodrošina automātisku strukturēšanu ar `pandas.json_normalize()`
- Validē datu saturu un saglabā reproducējamības metadatus
- Atbilst **FAIR principiem**: Findable, Accessible, Interoperable, Reusable

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

import json
import os
import pandas as pd
import datetime


def load_json_records(path: str, required_fields: list[str] | None = None) -> pd.DataFrame:
    """
    Ielādē JSON formāta ierakstus un pārveido tos DataFrame formātā.

    Parametri:
    -----------
    path : str
        Ceļš uz JSON failu.
    required_fields : list[str], optional
        Lauku saraksts, kas obligāti jāpārbauda (piemēram: ["patient_id", "sex_at_birth"])

    Atgriež:
    --------
    df : pd.DataFrame
        Ielādēta un normalizēta datu kopa ar FAIR reproducējamības metadatiem.
    """

    if not os.path.exists(path):
        raise FileNotFoundError(f"❌ JSON fails nav atrasts: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise RuntimeError(f"❌ Neizdevās nolasīt JSON failu: {e}")

    # Normalizē JSON struktūru
    try:
        df = pd.json_normalize(data)
    except Exception as e:
        raise ValueError(f"❌ JSON struktūras kļūda: {e}")

    # Pārbauda obligātos laukus
    if required_fields:
        missing = [c for c in required_fields if c not in df.columns]
        if missing:
            raise ValueError(f"⚠️ Trūkst obligātie lauki JSON datos: {missing}")

    # Izveido reproducējamības metadatus (FAIR un Data-Centric AI atbilstībai)
    meta = {
        "loader": "JSON",
        "path": os.path.abspath(path),
        "timestamp": datetime.datetime.now().isoformat(),
        "row_count": len(df),
        "columns": list(df.columns),
        "required_fields_checked": required_fields if required_fields else None,
        "source_type": "JSON file",
    }

    # Saglabā metadatus DataFrame atribūtos reproducējamībai
    df.attrs["meta"] = meta

    return df

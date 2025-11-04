"""
json_loader.py — JSON datu ielādes modulis

Šis modulis nodrošina JSON formāta datu ielādi un konvertēšanu pandas DataFrame formātā.
Atbalsta:
- standarta JSON masīvus,
- ligzdotus (nested) objektus,
- NDJSON (newline-delimited JSON) failus.

Funkcionālais mērķis:
1. Automātiski noteikt JSON datu struktūru (schema discovery).
2. Izvilkt ligzdotos laukus līdz tabulveida formātam.
3. Sagatavot datus AI datu kvalitātes novērtēšanai un imputācijai.

Akadēmiskais pamats:
- Abedjan, Z. et al. (2016). "Detecting Data Errors: The Systematic Approach".
- Batini & Scannapieco (2016). “Data and Information Quality”.
- FAIR Data Principles (Wilkinson et al., 2016)
"""

import json
import pandas as pd
import os
from typing import Dict, Any


def analyze_json_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Veic strukturālo analīzi ielādētajam DataFrame:
    - datu tipi,
    - trūkstošo vērtību īpatsvars,
    - unikālo vērtību īpatsvars.
    """
    schema = {}
    for col in df.columns:
        non_null = df[col].notnull().sum()
        schema[col] = {
            "dtype": str(df[col].dtype),
            "non_null_rate": round(non_null / len(df), 3) if len(df) else 0,
            "unique_rate": round(df[col].nunique() / len(df), 3) if len(df) else 0,
            "example_values": df[col].dropna().astype(str).head(3).tolist(),
        }
    return schema


def load_json_records(file_path: str) -> pd.DataFrame:
    """
    Ielādē JSON vai NDJSON datni un pārvērš to pandas DataFrame formātā.

    Parametri:
    -----------
    file_path : str
        Ceļš uz JSON/NDJSON failu

    Atgriež:
    --------
    pd.DataFrame — ielādētie dati
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Failu '{file_path}' nevar atrast.")

    # Pārbauda, vai fails ir NDJSON (viena JSON rinda)
    with open(file_path, "r", encoding="utf-8") as f:
        first_line = f.readline().strip()
        is_ndjson = first_line.startswith("{") and not first_line.endswith("}")

    try:
        if is_ndjson:
            # NDJSON režīms
            df = pd.read_json(file_path, lines=True)
        else:
            # Parasts JSON masīvs
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            df = pd.json_normalize(data)

    except Exception as e:
        raise ValueError(f"Neizdevās ielādēt JSON datus: {e}")

    if df.empty:
        raise ValueError("Ielādētie JSON dati ir tukši vai nederīgi.")

    # Strukturālā analīze
    schema = analyze_json_schema(df)
    print("JSON struktūras analīze (pirmie lauki):")
    for col, info in list(schema.items())[:5]:
        print(f"  {col}: {info}")

    return df


    # Saglabā metadatus DataFrame atribūtos reproducējamībai
    df.attrs["meta"] = meta

    return df

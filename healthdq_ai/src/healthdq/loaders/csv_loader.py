"""
csv_loader.py — CSV datu ielādes modulis

Šis modulis nodrošina drošu un automatizētu CSV datu ielādi,
atbalstot plašu formātu klāstu (UTF-8, semikols, komats, tab),
un sākotnēju strukturālo analīzi (Schema Discovery).

Funkcionālais mērķis:
1. Droša CSV ielāde neatkarīgi no faila formāta.
2. Automātiska datu tipu un struktūras noteikšana.
3. Saderība ar MI datu kvalitātes cauruļvadu (healthdq-ai).


"""

import pandas as pd
import os
from typing import Dict, Any

try:  # pragma: no cover - atkarība nav obligāta testos
    import chardet
except ImportError:  # pragma: no cover
    chardet = None


def detect_encoding(file_path: str) -> str:
    """Nosaka faila kodējumu (droši arī ne-UTF-8 gadījumos)."""
    if chardet is None:
        return "utf-8"

    with open(file_path, "rb") as f:
        result = chardet.detect(f.read(100000))
    return result["encoding"] or "utf-8"


def analyze_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Veic sākotnējo datu struktūras analīzi:
    - kolonnu tipi
    - unikālo vērtību īpatsvars
    - trūkstošo vērtību īpatsvars
    """
    schema = {}
    for col in df.columns:
        non_null = df[col].notnull().sum()
        schema[col] = {
            "dtype": str(df[col].dtype),
            "non_null_rate": round(non_null / len(df), 3) if len(df) else 0,
            "unique_rate": round(df[col].nunique() / len(df), 3) if len(df) else 0,
            "example_values": df[col].dropna().astype(str).head(3).tolist()
        }
    return schema


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Ielādē CSV datu kopu, neatkarīgi no kodējuma un atdalītāja,
    un atgriež DataFrame objektu.

    Parametri:
    -----------
    file_path: str — ceļš uz CSV failu

    Atgriež:
    --------
    pd.DataFrame — ielādētie dati
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Failu '{file_path}' nevar atrast.")

    encoding = detect_encoding(file_path)

    # mēģina atpazīt atdalītāju
    with open(file_path, "r", encoding=encoding, errors="ignore") as f:
        sample = f.readline()
    sep = ";" if ";" in sample else "," if "," in sample else "\t"

    df = pd.read_csv(file_path, sep=sep, encoding=encoding)
    if df.empty:
        raise ValueError("Ielādētais CSV fails ir tukšs vai neatpazīts.")

    # pievieno automātisku shēmas analīzi
    schema = analyze_schema(df)
    print("Datu struktūras analīze (pirmie lauki):")
    for col, info in list(schema.items())[:5]:
        print(f"  {col}: {info}")

    return df

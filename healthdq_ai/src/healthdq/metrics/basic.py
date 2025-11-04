"""
basic.py — Datu kvalitātes pamatmetrikas
=========================================

Šis modulis nodrošina pamatfunkcijas datu kvalitātes novērtēšanai, kas tiek
izmantotas visās trīs galvenajās dimensijās (Precision, Completeness, Reusability).

Mērķis:
--------
Nodrošināt mērāmu, reproducējamu un universālu datu kvalitātes pamata indikatoru aprēķinu.

Akadēmiskais pamats:
--------------------
- Wang, R.Y., & Strong, D.M. (1996). “Beyond Accuracy: What Data Quality Means to Data Consumers.”
- Batini, C., & Scannapieco, M. (2016). “Data and Information Quality.”
- Hinrichs, H. (2002). “Measuring completeness and consistency in data quality.”
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def not_null_rate(df: pd.DataFrame) -> float:
    """Aprēķina datu pilnīguma rādītāju (ne-tukšo vērtību īpatsvaru)."""
    total = df.size
    non_null = df.count().sum()
    return round(non_null / total, 4) if total else 0.0


def missing_value_ratio(df: pd.DataFrame) -> float:
    """Aprēķina trūkstošo vērtību īpatsvaru."""
    total = df.size
    missing = df.isna().sum().sum()
    return round(missing / total, 4) if total else 0.0


def out_of_range_rate(df: pd.DataFrame, ranges: Dict[str, Dict[str, Any]]) -> float:
    """
    Aprēķina ārpus diapazona esošo vērtību īpatsvaru pēc definētajiem noteikumiem.

    Parametri:
    -----------
    df : pd.DataFrame
        Ievades dati.
    ranges : dict
        Piemēram:
        {
            "height_cm": {"min": 40, "max": 250},
            "weight_kg": {"min": 1, "max": 400}
        }
    """
    if not ranges:
        return 0.0

    violations = 0
    total = 0

    for col, limits in ranges.items():
        if col not in df.columns:
            continue
        total += len(df[col])
        min_val = limits.get("min", -np.inf)
        max_val = limits.get("max", np.inf)
        violations += ((df[col] < min_val) | (df[col] > max_val)).sum()

    return round(violations / total, 4) if total else 0.0


def uniqueness_rate(df: pd.DataFrame, subset: list = None) -> float:
    """Aprēķina ierakstu unikālitātes īpatsvaru pēc noteiktām kolonnām."""
    if subset is None:
        subset = df.columns.tolist()
    unique_rows = df.drop_duplicates(subset=subset)
    return round(len(unique_rows) / len(df), 4) if len(df) else 0.0


def logical_consistency_rate(df: pd.DataFrame, formula: str, target_col: str, tolerance: float = 0.01) -> float:
    """
    Novērtē loģisko konsekvenci starp aprēķinātām un faktiskām vērtībām.

    Piemērs:
        formula = "weight_kg / ((height_cm/100)**2)"
        target_col = "bmi"
    """
    if target_col not in df.columns:
        return 0.0

    try:
        computed = df.eval(formula)
        actual = df[target_col]
        consistent = abs(computed - actual) <= (abs(actual) * tolerance)
        return round(consistent.mean(), 4)
    except Exception:
        return 0.0


def entropy_of_column(df: pd.DataFrame, col: str) -> float:
    """
    Aprēķina entropiju (H) kolonnai, kas norāda semantisko dispersiju.
    Zema entropija = augsta harmonizācija (reusability dimensija).
    """
    if col not in df.columns:
        return 0.0

    freq = df[col].value_counts(normalize=True)
    return round(-(freq * np.log2(freq + 1e-9)).sum(), 4)


def categorical_harmonization_rate(df: pd.DataFrame, semantic_map: Dict[str, str]) -> float:
    """
    Aprēķina semantiskās harmonizācijas rādītāju, salīdzinot ar mapējumu.

    Parametri:
    -----------
    semantic_map : dict
        Piemēram {"female": "F", "male": "M", "woman": "F"}
    """
    if not semantic_map:
        return 1.0

    total = 0
    matched = 0
    for col in df.columns:
        if df[col].dtype == "object":
            total += len(df[col])
            mapped_values = df[col].astype(str).map(semantic_map).notnull().sum()
            matched += mapped_values

    return round(matched / total, 4) if total else 1.0

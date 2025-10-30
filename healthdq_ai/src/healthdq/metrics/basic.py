"""
basic.py — Datu kvalitātes rādītāju bāzes aprēķini
=================================================

Šis modulis ietver pamatfunkcijas datu kvalitātes (DQ) metriku aprēķināšanai
veselības datu prototipam *healthdq-ai*, kas ir daļa no promocijas darba
“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai
atvērtās zinātnes iniciatīvās”.

Funkcionalitāte:
----------------
- Aprēķina bāzes kvalitātes rādītājus:
    * not_null_rate (pilnīguma indikators)
    * out_of_range_rate (precizitātes indikators)
    * semantic_standardization_rate (atkārtotas izmantojamības indikators)
    * logical_consistency_rate (loģiskā atbilstība, piem. BMI)
- Nodrošina FAIR reproducējamību, pievienojot metadatus katram mērījumam
- Lietojams citu modulu (precision_metrics, completeness_metrics, reusability_metrics) ietvaros

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

import pandas as pd
import numpy as np
import datetime


def metric_record(name: str, value: float, columns=None, dimension=None, stage="raw"):
    """Izveido strukturētu mērījuma ierakstu ar FAIR metadatiem."""
    return {
        "metric_name": name,
        "value": round(float(value), 4),
        "dimension": dimension,
        "columns": columns,
        "timestamp": datetime.datetime.now().isoformat(),
        "source_stage": stage
    }


# ---------------------------------------------------------------------
# COMPLETENESS (pilnīgums)
# ---------------------------------------------------------------------
def not_null_rate(df: pd.DataFrame, columns: list[str]) -> dict:
    """Aprēķina to rindu proporciju, kurās nav trūkstošu vērtību."""
    subset = df[columns]
    rate = subset.notnull().mean().mean()
    return metric_record("not_null_rate", rate, columns, "completeness")


def missingness_index(df: pd.DataFrame, columns: list[str]) -> dict:
    """Trūkstošo vērtību īpatsvars (1 - not_null_rate)."""
    rate = 1 - df[columns].notnull().mean().mean()
    return metric_record("missingness_index", rate, columns, "completeness")


# ---------------------------------------------------------------------
# PRECISION (precizitāte un loģiskā korektība)
# ---------------------------------------------------------------------
def out_of_range_rate(df: pd.DataFrame, column: str, min_val: float, max_val: float) -> dict:
    """Aprēķina vērtību proporciju ārpus noteiktā diapazona."""
    valid_mask = df[column].between(min_val, max_val, inclusive="both")
    rate = 1 - valid_mask.mean()
    return metric_record("out_of_range_rate", rate, [column], "precision")


def logical_consistency_rate(df: pd.DataFrame, weight_col: str, height_col: str, bmi_col: str, tolerance=0.25) -> dict:
    """
    Novērtē loģisko atbilstību starp svars, augums un BMI kolonnām.
    Tolerance ±25% pēc noklusējuma.
    """
    bmi_calc = df[weight_col] / ((df[height_col] / 100) ** 2)
    consistent = (abs(bmi_calc - df[bmi_col]) / df[bmi_col]) <= tolerance
    rate = consistent.mean()
    return metric_record("logical_consistency_rate", rate, [weight_col, height_col, bmi_col], "precision")


# ---------------------------------------------------------------------
# REUSABILITY (atkārtota izmantojamība, semantika)
# ---------------------------------------------------------------------
def semantic_standardization_rate(df: pd.DataFrame, column: str, mapping: dict) -> dict:
    """
    Novērtē, cik liela daļa vērtību tika veiksmīgi saskaņotas ar semantisko karti.
    """
    standardized = df[column].map(mapping).notnull()
    rate = standardized.mean()
    return metric_record("semantic_standardization_rate", rate, [column], "reusability")


def categorical_consistency(df: pd.DataFrame, column: str) -> dict:
    """Vienkāršs rādītājs: unikālo kategoriju skaits (jo mazāks, jo labāk strukturēts)."""
    unique_ratio = len(df[column].dropna().unique()) / len(df)
    return metric_record("categorical_consistency", unique_ratio, [column], "reusability")


# ---------------------------------------------------------------------
# UNIVERSĀLĀ KOPSAVILKUMA FUNKCIJA
# ---------------------------------------------------------------------
def summarize_metrics(metrics_list: list[dict]) -> pd.DataFrame:
    """
    Apvieno vairākus metriku ierakstus DataFrame formā.
    Lieto iekšēji katra aģenta (agent) “report” posmā.
    """
    return pd.DataFrame(metrics_list)

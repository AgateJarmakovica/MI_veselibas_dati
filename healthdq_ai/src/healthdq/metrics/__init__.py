"""
healthdq.metrics — Datu kvalitātes metrikas modulis
===================================================

Šis modulis nodrošina datu kvalitātes metriku aprēķinu pirms un pēc
AI apstrādes posmiem (Precision, Completeness, Reusability).

Akadēmiskais pamats:
--------------------
- Batini & Scannapieco (2016): “Data and Information Quality”
- Wang & Strong (1996): “Beyond Accuracy: What Data Quality Means to Data Consumers”
- Hinrichs (2002): “Measuring completeness and consistency in data quality”
- FAIR & Data-Centric AI principu ievērošana

Mērķis:
--------
Kvantitatīvi novērtēt, cik lielā mērā dati ir uzlaboti pēc AI balstītas apstrādes.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def completeness_rate(df: pd.DataFrame) -> float:
    """Aprēķina datu pilnīguma rādītāju (ne-tukšo vērtību īpatsvars)."""
    total = df.size
    non_null = df.count().sum()
    return round(non_null / total, 4) if total else 0.0


def precision_rate(before: pd.DataFrame, after: pd.DataFrame) -> float:
    """
    Salīdzina datu precizitāti pirms un pēc tīrīšanas,
    aprēķinot vērtību izmaiņu īpatsvaru.
    """
    common_cols = [col for col in before.columns if col in after.columns]
    if not common_cols:
        return 0.0

    diffs = (before[common_cols] != after[common_cols]).sum().sum()
    total = before[common_cols].size
    return round(1 - (diffs / total), 4) if total else 0.0


def reusability_score(df: pd.DataFrame) -> float:
    """
    Novērtē semantisko saskaņotību un vienotu vērtību lietojumu.
    Augstāka vērtība nozīmē mazāku unikālo kategoriju entropiju.
    """
    cat_cols = df.select_dtypes(include=["object", "category"]).columns
    if not len(cat_cols):
        return 1.0

    entropy_sum = 0
    for col in cat_cols:
        freq = df[col].value_counts(normalize=True)
        entropy = -(freq * np.log2(freq + 1e-9)).sum()
        entropy_sum += entropy

    norm_entropy = entropy_sum / len(cat_cols)
    return round(1 - min(norm_entropy / 10, 1), 4)  # 0–1 normalizācija


def compute_metrics(before: pd.DataFrame, after: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Aprēķina vispārīgās un konfigurācijā definētās datu kvalitātes metrikas.

    Parametri:
    -----------
    before : pd.DataFrame — dati pirms apstrādes
    after : pd.DataFrame — dati pēc apstrādes
    config : dict — konfigurācijas dati (rules.yml vai AI noteikumi)

    Atgriež:
    --------
    dict — metriku kopsavilkums (pirms/pēc)
    """
    metrics = {
        "completeness_before": completeness_rate(before),
        "completeness_after": completeness_rate(after),
        "precision_retention": precision_rate(before, after),
        "reusability_after": reusability_score(after),
    }

    # Papildu metrikas no konfigurācijas faila, ja tādas definētas
    if "metrics" in config:
        for metric in config["metrics"]:
            m_name = metric.get("name")
            m_type = metric.get("type")

            if m_type == "not_null_rate":
                cols = metric.get("columns", [])
                val = after[cols].notnull().mean().mean() if cols else completeness_rate(after)
                metrics[m_name] = round(float(val), 4)

            elif m_type == "out_of_range_rate":
                cols = metric.get("columns", [])
                val = 0
                for c in cols:
                    if c in after.columns:
                        col_min, col_max = after[c].min(), after[c].max()
                        if np.isfinite(col_min) and np.isfinite(col_max):
                            val += ((after[c] < col_min) | (after[c] > col_max)).mean()
                metrics[m_name] = round(float(val / len(cols)), 4) if cols else 0.0

            elif m_type == "categorical_standardization_rate":
                cols = metric.get("columns", [])
                val = 0
                for c in cols:
                    if c in after.columns:
                        val += after[c].nunique() / len(after[c].dropna())
                metrics[m_name] = round(1 - (val / len(cols)), 4) if cols else 0.0

    return metrics


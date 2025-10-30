"""
transform.py — Datu kvalitātes transformācijas funkcijas
=========================================================

Šis modulis ietver datu transformācijas funkcijas, kas uzlabo veselības datu
kvalitāti atbilstoši *healthdq-ai* prototipam — promocijas darba
“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai
atvērtās zinātnes iniciatīvās” ietvaros.

Mērķis:
--------
Veikt AI-atbalstītas datu transformācijas, kas uzlabo trīs datu kvalitātes dimensijas:
  - **Precizitāti** (atvasināto vērtību loģiskā saskaņa, piemēram, BMI)
  - **Pilnīgumu** (imputācija — trūkstošo vērtību aizpildīšana)
  - **Atkārtotu izmantojamību** (semantiskā harmonizācija un standartizācija)

Funkcijas:
-----------
- `harmonize_semantics()` — pārveido semantiski līdzīgus terminus uz standartizētu formu
- `impute_simple()` — aizpilda trūkstošās vērtības ar vidējo, modi vai atvasināto vērtību
- `compute_bmi()` — aprēķina ķermeņa masas indeksu (BMI) no auguma un svara datiem

Visas funkcijas atbilst **FAIR datu principiem** un pievieno reproducējamības metadatus.

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

import pandas as pd
import numpy as np
import datetime


# ---------------------------------------------------------------------
# SEMANTISKĀ HARMONIZĀCIJA
# ---------------------------------------------------------------------
def harmonize_semantics(df: pd.DataFrame, semantic_maps: dict) -> pd.DataFrame:
    """
    Semantiski harmonizē (vienādo) kategoriskās vērtības pēc noteiktām kartēm.
    Piemēram, “female”, “woman”, “F” → “F”.

    Parametri:
    -----------
    df : pd.DataFrame
        Datu kopa
    semantic_maps : dict
        Kartes no `rules.yml` sadaļas "semantic_maps"

    Atgriež:
    --------
    pd.DataFrame ar harmonizētām vērtībām un reproducējamības metadatiem.
    """
    df = df.copy()
    applied_maps = []

    for col, mapping in semantic_maps.items():
        if col in df.columns:
            applied_maps.append(col)
            df[col] = df[col].map(mapping).fillna(df[col])

    df.attrs["meta"] = {
        "transform": "semantic_harmonization",
        "columns_modified": applied_maps,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    return df


# ---------------------------------------------------------------------
# BMI APRĒĶINS (ATVASINĀTĀ VĒRTĪBA)
# ---------------------------------------------------------------------
def compute_bmi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aprēķina ķermeņa masas indeksu (BMI) no auguma un svara datiem, ja tie ir pieejami.
    Aizpilda trūkstošās BMI vērtības gadījumos, kad augums un svars ir zināmi.

    Formula:
    --------
    BMI = weight_kg / (height_cm / 100)^2

    Atgriež:
    --------
    pd.DataFrame ar papildinātu "bmi" kolonnu un metadatiem reproducējamībai.
    """
    df = df.copy()
    if {"height_cm", "weight_kg"}.issubset(df.columns):
        # Nosaka, kur nepieciešams aprēķināt BMI
        need = (
            df["height_cm"].notna()
            & df["weight_kg"].notna()
            & (df.get("bmi").isna() if "bmi" in df.columns else True)
        )
        df.loc[need, "bmi"] = (
            df.loc[need, "weight_kg"]
            / ((df.loc[need, "height_cm"] / 100) ** 2)
        ).round(2)

        df.attrs["meta"] = {
            "transform": "compute_bmi",
            "rows_computed": int(need.sum()),
            "timestamp": datetime.datetime.now().isoformat(),
        }

    return df


# ---------------------------------------------------------------------
# VIENKĀRŠĀ IMPUTĀCIJA (MISSING VALUE HANDLING)
# ---------------------------------------------------------------------
def impute_simple(df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """
    Veic trūkstošo vērtību aizpildīšanu pēc noteiktas stratēģijas.
    Atbalstītās stratēģijas:
      - "median" — aizpilda ar mediānu
      - "mode" — aizpilda ar modi (visbiežāko vērtību)
      - "compute_from_height_weight" — aprēķina BMI no auguma/svara

    Parametri:
    -----------
    df : pd.DataFrame
        Datu kopa
    strategy : dict
        Stratēģijas no `rules.yml` sadaļas "imputation.strategy"

    Atgriež:
    --------
    pd.DataFrame ar aizpildītām vērtībām un metadatiem reproducējamībai.
    """
    df = df.copy()
    imputed_cols = []

    for col, strat in strategy.items():
        if col not in df.columns:
            continue

        if strat == "median":
            val = df[col].median(skipna=True)
            df[col] = df[col].fillna(val)
            imputed_cols.append(col)

        elif strat == "mode":
            val = df[col].mode(dropna=True)
            val = val.iloc[0] if len(val) > 0 else None
            df[col] = df[col].fillna(val)
            imputed_cols.append(col)

        elif strat == "compute_from_height_weight":
            df = compute_bmi(df)
            imputed_cols.append("bmi")

        elif isinstance(strat, dict) and strat.get("method") == "conditional_compute":
            condition = strat.get("condition")
            formula = strat.get("formula")
            try:
                mask = df.eval(condition.replace("if ", ""))
                df.loc[mask, col] = df.loc[mask].eval(formula).round(2)
                imputed_cols.append(col)
            except Exception as e:
                print(f"⚠️ Error in conditional computation for {col}: {e}")

    df.attrs["meta"] = {
        "transform": "imputation",
        "columns_imputed": imputed_cols,
        "timestamp": datetime.datetime.now().isoformat(),
    }
    return df


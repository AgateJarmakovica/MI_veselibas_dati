"""
CompletenessAgent
=================

Šis modulis īsteno veselības datu kvalitātes uzlabošanas aģentu,
kas fokusējas uz **pilnīguma dimensiju (Completeness)** — vienu no trim
galvenajām datu kvalitātes dimensijām promocijas darba “healthdq-ai” prototipā.

Galvenais mērķis:
-----------------
Uzlabot veselības datu kopu pilnīgumu, izmantojot
mākslīgā intelekta (MI) atbalstītu imputācijas (aizpildes) pieeju.
Risinājums darbojas saskaņā ar FAIR principiem un Data-Centric AI paradigmu,
nodrošinot reproducējamību un semantisko izsekojamību (`derived_from` metadatus).

Darbības soļi:
--------------
1. Nolasa `rules.yml` faila sadaļu `imputation.strategy`
2. Izpilda atbilstošo trūkstošo vērtību aizpildīšanu (median, mode, vai BMI formula)
3. Saglabā imputācijas žurnālu un reproducējamības metadatus
4. Atgriež uzlaboto DataFrame + metadatus nākamajam validācijas posmam

Autore: Agate Jarmakoviča
Versija: 1.2
Datums: 2025-10-30
"""

import pandas as pd
import datetime
from ..rules import impute_simple


class CompletenessAgent:
    """
    CompletenessAgent klase veic trūkstošo vērtību aizpildīšanu veselības datos.
    Tā uzlabo datu pilnīgumu, izmantojot noteikumos (`rules.yml`) definētās
    imputācijas stratēģijas (piemēram, median, mode vai atvasinātās formulas).

    Aģents arī ģenerē žurnālu (`log`) un reproducējamības metadatus (`meta`),
    kas nodrošina datu izsekojamību un pārskatāmību atvērtās zinātnes iniciatīvās.
    """

    def __init__(self, config: dict, version: str = "1.2"):
        self.config = config
        self.version = version

    def run(self, df: pd.DataFrame):
        """
        Izpilda pilnīguma uzlabošanas posmu:
        - pielieto imputācijas stratēģiju no konfigurācijas (`rules.yml`)
        - saglabā reproducējamības metadatus un žurnālu

        Parametri:
        -----------
        df : pd.DataFrame
            Datu kopa, kurā tiks veikta imputācija

        Atgriež:
        --------
        df_imp : pd.DataFrame
            Datu kopa ar aizpildītām trūkstošajām vērtībām
        log : list[dict]
            Imputācijas notikumu žurnāls
        meta : dict
            Reproducējamības metadati (versija, stratēģija, timestamp, derived_from)
        """
        strategy = self.config.get("imputation", {}).get("strategy", {})
        if not strategy:
            raise ValueError("❌ Imputation strategy nav definēta konfigurācijā (rules.yml).")

        try:
            df_imp, log = impute_simple(df, strategy)
        except Exception as e:
            raise RuntimeError(f"❌ Imputation kļūda: {e}")

        # Izveido reproducējamības metadatus
        meta = {
            "agent": "CompletenessAgent",
            "calc_version": self.version,
            "imputation_policy": strategy,
            "timestamp": datetime.datetime.now().isoformat(),
            "derived_from": [c for c in df.columns if "bmi" in c.lower()]
        }

        # Pievieno informāciju datu ietvarā (papildu caurspīdībai)
        df_imp.attrs["completeness_meta"] = meta

        return df_imp, log, meta


# ------------------------------------------------------------
# Palīgfunkcija (var būt arī rules/impute_simple.py failā)
# ------------------------------------------------------------
def impute_simple(df: pd.DataFrame, strategy: dict):
    """
    Vienkārša imputācijas metode, kas realizē noteikumos definētās stratēģijas:
    - median
    - mode
    - compute_from_height_weight (BMI gadījums)
    """
    log = []
    df = df.copy()

    for col, method in strategy.items():
        if col not in df.columns:
            continue

        missing = int(df[col].isnull().sum())
        if missing == 0:
            continue

        if method == "median":
            fill_value = df[col].median()
        elif method == "mode":
            fill_value = df[col].mode().iloc[0]
        elif method == "compute_from_height_weight":
            if "height_cm" in df.columns and "weight_kg" in df.columns:
                fill_value = df["weight_kg"] / ((df["height_cm"] / 100) ** 2)
            else:
                continue
        else:
            continue

        df[col] = df[col].fillna(fill_value)
        log.append({
            "column": col,
            "method": method,
            "filled": missing,
            "fill_value": str(fill_value)[:20]
        })

    return df, log

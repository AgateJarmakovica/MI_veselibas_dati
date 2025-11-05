"""
transform.py — Inteliģentās datu transformācijas dzinējs
=========================================================

Šis modulis veic veselības (vai citu tipu) datu transformācijas,
izmantojot gan noteikumus no konfigurācijas (`rules.yml`), gan
pašmācības rezultātus no `rule_learning.py`.

Galvenās funkcijas:
-------------------
- Datu aizpildīšana (imputācija)
- Harmonizācija (terminu, vienību, vērtību saskaņošana)
- Datu normalizācija un standartizācija
- Transformāciju vēstures saglabāšana reproducējamībai
- HITL (Human-in-the-Loop) labojumu integrācija

Atbilst FAIR un Data-Centric AI principiem.
"""

import pandas as pd
import numpy as np
import json
from datetime import datetime
from pathlib import Path


class DataTransformer:
    """
    Galvenā klase, kas piemēro datu kvalitātes transformācijas,
    balstoties uz konfigurāciju un automātiski ģenerētiem noteikumiem.
    """

    def __init__(self, config: dict, feedback_path: str = "out/hitl_feedback.json"):
        self.config = config
        self.feedback_path = feedback_path
        self.history = []

    # ------------------------------------------------------------------
    # IMPUTATION — trūkstošo vērtību aizpildīšana
    # ------------------------------------------------------------------
    def impute_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        impute_cfg = self.config.get("imputation", {})
        methods = impute_cfg.get("methods", {})
        ai_support = impute_cfg.get("ai_support", {}).get("enabled", False)

        for col in df.columns:
            missing = df[col].isna().sum()
            if missing == 0:
                continue

            dtype = str(df[col].dtype)
            if "float" in dtype or "int" in dtype:
                method = methods.get("numerical", "median")
                if method == "median":
                    fill_value = df[col].median()
                elif method == "mean":
                    fill_value = df[col].mean()
                else:
                    fill_value = df[col].interpolate().bfill().ffill().median()
                df[col] = df[col].fillna(fill_value)

            elif "datetime" in dtype:
                method = methods.get("datetime", "interpolate")
                if method == "interpolate":
                    df[col] = df[col].interpolate(method="time")

            else:
                method = methods.get("categorical", "mode")
                if method == "mode":
                    fill_value = df[col].mode().iloc[0] if not df[col].mode().empty else "Unknown"
                    df[col] = df[col].fillna(fill_value)

            self.history.append({
                "step": "imputation",
                "column": col,
                "missing_filled": int(missing),
                "timestamp": datetime.now().isoformat(),
                "method": method,
            })

        if ai_support:
            self._apply_ai_imputation(df)

        return df

    # ------------------------------------------------------------------
    # AI IMPUTATION — kontekstuāla trūkstošo vērtību prognozēšana
    # ------------------------------------------------------------------
    def _apply_ai_imputation(self, df: pd.DataFrame):
        """
        Šī metode ir vieta MI modeļa integrācijai (piem., maza LLM vai tabulārais modelis),
        kas var prognozēt trūkstošās vērtības, izmantojot citu kolonnu kontekstu.
        Šobrīd paredzēta integrācijai ar ārēju API vai lokālu modeli.
        """
        self.history.append({
            "step": "ai_imputation",
            "description": "AI imputācija (paredzētās vērtības tiks pievienotas nākotnē)",
            "timestamp": datetime.now().isoformat(),
        })

    # ------------------------------------------------------------------
    # SEMANTIC HARMONIZATION — vērtību saskaņošana
    # ------------------------------------------------------------------
    def harmonize_values(self, df: pd.DataFrame) -> pd.DataFrame:
        sem_cfg = self.config.get("reusability", {})
        if not sem_cfg.get("enabled", False):
            return df

        mapping_data = sem_cfg.get("mapping_learning", {})
        if not mapping_data:
            return df

        ontology_ref = mapping_data.get("training_data", None)
        if ontology_ref and Path(ontology_ref).exists():
            with open(ontology_ref, "r", encoding="utf-8") as f:
                ontology = json.load(f)
        else:
            ontology = {}

        for col in df.columns:
            if col in ontology:
                df[col] = df[col].replace(ontology[col])

        self.history.append({
            "step": "semantic_harmonization",
            "columns_updated": list(df.columns),
            "timestamp": datetime.now().isoformat(),
        })
        return df

    # ------------------------------------------------------------------
    # NORMALIZATION — vērtību mērogošana un loģiskā standartizācija
    # ------------------------------------------------------------------
    def normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in df.select_dtypes(include=["float", "int"]).columns:
            if df[col].std() > 0:
                df[col] = (df[col] - df[col].mean()) / df[col].std()
        self.history.append({
            "step": "normalization",
            "columns_normalized": list(df.select_dtypes(include=["float", "int"]).columns),
            "timestamp": datetime.now().isoformat(),
        })
        return df

    # ------------------------------------------------------------------
    # REPRODUCIBILITY METADATA
    # ------------------------------------------------------------------
    def save_history(self, out_dir: str = "out"):
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        with open(f"{out_dir}/transform_history.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)


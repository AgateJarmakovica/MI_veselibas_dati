"""
reusability.py — Atkārtotas izmantojamības aģents veselības datu kvalitātei

Šis modulis realizē datu kvalitātes dimensiju “Atkārtota izmantojamība” (Reusability),
kas saskaņā ar FAIR un Data-Centric AI principiem nodrošina semantisku harmonizāciju
un datu vienotību. Tas veic terminoloģijas standartizāciju, vērtību kartēšanu un
datu harmonizāciju, izmantojot konfigurācijas failā noteiktas semantiskās kartes.

Akadēmiskais pamatojums:
- Wilkinson, M. D. et al. (2016). "The FAIR Guiding Principles for scientific data management and stewardship."
- Batini, C. & Scannapieco, M. (2016). "Data and Information Quality."
- Assante, M. et al. (2020). "Enabling FAIR Data Reuse in Health Research."

Šis aģents kalpo kā datu semantiskās harmonizācijas slānis pirms analīzes vai imputācijas.
"""

import pandas as pd
from typing import Dict, Any, List
import logging
import os


class ReusabilityAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.semantic_maps = config.get("semantic_maps", {})
        self.output_dir = "out/logs"
        os.makedirs(self.output_dir, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(self.output_dir, "reusability_agent.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        logging.info("ReusabilityAgent started semantic harmonization.")

        for column, mapping in self.semantic_maps.items():
            if column in df.columns:
                df[column] = df[column].astype(str).map(mapping).fillna(df[column])
                logging.info(f"Column '{column}' harmonized using semantic map ({len(mapping)} entries).")
            else:
                logging.warning(f"Column '{column}' not found in dataset, skipped harmonization.")

        df = self._normalize_text_fields(df)
        df = self._standardize_column_names(df)

        logging.info("ReusabilityAgent completed harmonization.")
        return df

    def _normalize_text_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nodrošina konsekventu tekstu formatējumu (mazie burti, apgriezti atstarpes)."""
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        return df

    def _standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Nodrošina kolonu nosaukumu saskaņošanu (mazie burti, bez atstarpēm)."""
        df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
        return df

    def evaluate_reusability_score(self, df: pd.DataFrame) -> float:
        """
        Aprēķina semantiskās saskaņotības rādītāju.
        Šis rādītājs mēra, cik lielā mērā vērtības atbilst definētajām semantiskajām kartēm.
        """
        total_values = 0
        matched_values = 0

        for column, mapping in self.semantic_maps.items():
            if column not in df.columns:
                continue
            mapped_values = df[column].astype(str).isin(mapping.values())
            total_values += len(df[column])
            matched_values += mapped_values.sum()

        if total_values == 0:
            return 0.0

        score = matched_values / total_values
        logging.info(f"Reusability harmonization success rate: {score:.4f}")
        return score

    return df, log

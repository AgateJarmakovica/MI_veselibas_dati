"""
healthdq.agents.completeness — Datu pilnīguma (Completeness) MI aģents
======================================================================

Šis modulis realizē mākslīgā intelekta aģentu, kas novērtē un uzlabo datu
pilnīgumu veselības datu kvalitātes cauruļvadā (pipeline).

Mērķis:
--------
Identificēt un aizpildīt trūkstošās vērtības (missing data), izmantojot
statistiskās un MI-atbalstītās imputācijas metodes, balstoties uz
Data-Centric AI principiem.

Metodes:
---------
1. Statistiskā imputācija (median, mode, interpolate)
2. AI-atbalstīta imputācija (semantic prediction)
3. Kombinētā pieeja (hybrid_semantic), kas izmanto abas

Autore: Agate Jarmakoviča  
Versija: 2.0  
Datums: 2025-10-30
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
from datetime import datetime
import logging


class CompletenessAgent:
    """
    CompletenessAgent — datu pilnīguma novērtēšanas un uzlabošanas aģents.

    Šī klase ir daļa no Data-Centric AI arhitektūras, un tā īsteno
    hibrīdu pieeju trūkstošo datu noteikšanai un aizpildīšanai.

    Parametri
    ----------
    config : dict
        Sistēmas konfigurācija, kas tiek ielādēta no rules.yml
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.settings = config.get("imputation", {})
        self.ai_support = self.settings.get("ai_support", {}).get("enabled", False)
        self.log_path = self.settings.get("logging", {}).get("output_dir", "out/imputation_logs/")
        self._init_logger()

    def _init_logger(self):
        """Inicializē žurnālu reproducējamībai."""
        logging.basicConfig(
            filename=f"{self.log_path}/completeness_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log",
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s"
        )
        logging.info("CompletenessAgent inicializēts.")

    def _detect_missing(self, df: pd.DataFrame) -> pd.Series:
        """Atgriež kopsavilkumu par trūkstošajām vērtībām katrā kolonnā."""
        missing = df.isnull().sum()
        logging.info(f"Trūkstošo vērtību noteikšana: {missing.to_dict()}")
        return missing

    def _statistical_impute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aizpilda trūkstošās vērtības, izmantojot statistiskās metodes."""
        methods = self.settings.get("methods", {})
        for col in df.columns:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    if methods.get("numerical") == "median":
                        fill_value = df[col].median()
                    elif methods.get("numerical") == "mean":
                        fill_value = df[col].mean()
                    else:
                        fill_value = df[col].mode().iloc[0]
                    df[col].fillna(fill_value, inplace=True)
                elif pd.api.types.is_datetime64_any_dtype(df[col]):
                    if methods.get("datetime") == "interpolate":
                        df[col] = df[col].interpolate()
                else:
                    df[col].fillna(df[col].mode().iloc[0], inplace=True)
                logging.info(f"Kolonna '{col}' aizpildīta ar statistisko metodi.")
        return df

    def _ai_semantic_impute(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Piemēro MI modeli, lai paredzētu trūkstošās vērtības, pamatojoties uz
        citu kolonnu semantiskajām attiecībām.
        """
        try:
            from transformers import pipeline
            model_name = self.settings.get("ai_support", {}).get("model_name", "microsoft/phi-2")
            predictor = pipeline("text-generation", model=model_name)
        except Exception as e:
            logging.error(f"AI modeļa ielādes kļūda: {e}")
            return df

        for col in df.columns:
            if df[col].isnull().any():
                prompt = f"Predict likely value for column '{col}' based on dataset semantics."
                for idx in df[df[col].isnull()].index:
                    context = df.loc[idx].dropna().to_dict()
                    try:
                        pred = predictor(f"{prompt}\nContext: {context}", max_new_tokens=10)[0]['generated_text']
                        df.at[idx, col] = pred.strip()
                        logging.info(f"AI imputācija kolonnai '{col}' rindā {idx}: {pred}")
                    except Exception as e:
                        logging.warning(f"AI imputācija neveiksmīga kolonnai '{col}', rinda {idx}: {e}")
        return df

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Izpilda pilnīguma pārbaudi un imputāciju.

        Darbības secība:
        1. Trūkstošo vērtību noteikšana.
        2. Statistiskā imputācija.
        3. AI semantiskā imputācija (ja iespējams).
        4. Reproducējamības žurnālu saglabāšana.
        """
        logging.info("Datu pilnīguma novērtēšanas posms uzsākts.")
        missing_before = self._detect_missing(df)

        df_imputed = self._statistical_impute(df.copy())
        if self.ai_support:
            df_imputed = self._ai_semantic_impute(df_imputed)

        missing_after = self._detect_missing(df_imputed)

        summary = {
            "missing_before": missing_before.to_dict(),
            "missing_after": missing_after.to_dict(),
        }
        logging.info(f"Imputācijas rezultātu kopsavilkums: {summary}")

        return df_imputed

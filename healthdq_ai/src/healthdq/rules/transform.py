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


def compute_bmi(
    df: pd.DataFrame,
    *,
    height_col: str = "height_cm",
    weight_col: str = "weight_kg",
    target_col: str = "bmi",
    round_decimals: int = 2,
) -> pd.DataFrame:
    """Aprēķina ķermeņa masas indeksu (ĶMI/BMI) pēc auguma un svara kolonnām.

    Funkcija neveic mutācijas uz ievades ``DataFrame`` – tā atgriež kopiju, kurā
    ``target_col`` satur aprēķināto BMI vērtību. Atbalsta scenārijus, kad augums
    norādīts centimetros (``> 10``) vai metros.

    Raises
    ------
    KeyError
        Ja trūkst norādītās auguma vai svara kolonnas.
    """

    missing = [col for col in (height_col, weight_col) if col not in df.columns]
    if missing:
        raise KeyError(f"Trūkst kolonnu BMI aprēķinam: {', '.join(missing)}")

    result = df.copy()
    heights = pd.to_numeric(result[height_col], errors="coerce")
    weights = pd.to_numeric(result[weight_col], errors="coerce")

    heights_m = heights.where(heights <= 10, heights / 100)
    heights_m = heights_m.mask(heights_m <= 0)

    bmi_values = weights / np.square(heights_m)
    bmi_values = bmi_values.replace([np.inf, -np.inf], np.nan)

    if target_col not in result.columns:
        result[target_col] = np.nan

    result[target_col] = result[target_col].where(result[target_col].notna(), bmi_values)
    if round_decimals is not None:
        result[target_col] = result[target_col].round(round_decimals)

    return result


def harmonize_semantics(
    df: pd.DataFrame,
    mappings: dict[str, dict],
    *,
    case_insensitive: bool = True,
) -> pd.DataFrame:
    """Harmonizē kategoriskās vērtības saskaņā ar konfigurācijas kartējumiem.

    ``mappings`` ir vārdnīca: ``{kolonna: {veco_vērtību: jauna_vērtība}}``. Funkcija
    atgriež ``DataFrame`` kopiju, saglabājot nemainīgas vērtības, kurām nav
    definēta kartēšana.

    Raises
    ------
    KeyError
        Ja ``mappings`` satur kolonnu, kas nav atrodama ``df``.
    """

    result = df.copy()

    for column, mapping in mappings.items():
        if column not in result.columns:
            raise KeyError(f"Kolonna '{column}' nav atrodama datu kopā.")

        if not isinstance(mapping, dict):
            raise TypeError(f"Kartējumam kolonnai '{column}' jābūt dict tipa.")

        if case_insensitive:
            lowered_map = {str(k).lower(): v for k, v in mapping.items()}

            def _replace(value):
                if pd.isna(value):
                    return value
                return lowered_map.get(str(value).lower(), value)

            result[column] = result[column].apply(_replace)
        else:
            result[column] = result[column].map(lambda v: mapping.get(v, v))

    return result


def impute_simple(
    df: pd.DataFrame,
    strategy: dict[str, str],
    *,
    constants: dict | None = None,
) -> pd.DataFrame:
    """Vienkārša trūkstošo vērtību imputācija, balstoties uz stratēģiju vārdnīcu.

    Atbalstītie paņēmieni: ``median``, ``mean``, ``mode``, ``ffill``, ``bfill`` un
    ``constant`` (vērtība tiek meklēta ``constants`` vārdnīcā).

    Raises
    ------
    KeyError
        Ja stratēģijā norādītā kolonna neeksistē ``df``.
    ValueError
        Ja ``constant`` stratēģijai nav pieejama vērtība vai stratēģija nav zināma.
    """

    result = df.copy()

    for column, method in strategy.items():
        if column not in result.columns:
            raise KeyError(f"Kolonna '{column}' nav atrodama datu kopā.")

        series = result[column]
        if method == "median":
            fill_value = series.median()
            result[column] = series.fillna(fill_value)
        elif method == "mean":
            fill_value = series.mean()
            result[column] = series.fillna(fill_value)
        elif method == "mode":
            mode_series = series.mode(dropna=True)
            if mode_series.empty:
                raise ValueError(f"Kolonnai '{column}' nav iespējams noteikt modi.")
            result[column] = series.fillna(mode_series.iloc[0])
        elif method == "ffill":
            result[column] = series.ffill()
        elif method == "bfill":
            result[column] = series.bfill()
        elif method == "constant":
            if not constants or column not in constants:
                raise ValueError(
                    f"Kolonnai '{column}' nav definēta konstanta vērtība imputācijai."
                )
            result[column] = series.fillna(constants[column])
        else:
            raise ValueError(f"Nezināma imputācijas metode kolonnai '{column}': {method}")

    return result


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


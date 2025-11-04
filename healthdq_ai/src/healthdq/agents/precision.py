"""
precision.py — Precizitātes aģents veselības datu kvalitātes novērtēšanai

Šis modulis realizē datu kvalitātes dimensiju “Precizitāte” (Precision),
kas saskaņā ar Batini & Scannapieco (2016) un Redman (2005) tiek definēta
kā datu loģiskās un semantiskās atbilstības novērtējums.
Aģents pārbauda loģiskās sakarības, vērtību korektumu un atklāj anomālijas.

Akadēmiskais pamatojums:
- Redman, T. C. (2005). "Measuring Data Accuracy: A Framework and Review."
- Batini, C., & Scannapieco, M. (2016). "Data and Information Quality."
- Wang, R. Y., & Strong, D. M. (1996). "Beyond Accuracy: What Data Quality Means to Data Consumers."

Šis aģents ir daļa no datu centrētās (Data-Centric AI) arhitektūras.
Tas izmanto noteikumus (rules.yml) un var tikt paplašināts ar MI modeli
anomāliju noteikšanai nākotnē.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging
import os


class PrecisionAgent:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules = config.get("rules", [])
        self.output_dir = "out/logs"
        os.makedirs(self.output_dir, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(self.output_dir, "precision_agent.log"),
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def run(self, df: pd.DataFrame) -> pd.DataFrame:
        issues = []
        for rule in self.rules:
            rule_type = rule.get("type")
            column = rule.get("column")

            if rule_type == "categorical":
                issues += self._check_categorical(df, rule)
            elif rule_type == "range":
                issues += self._check_range(df, rule)
            elif rule_type == "nonnegative":
                issues += self._check_nonnegative(df, rule)
            elif rule_type == "date_in_past":
                issues += self._check_date_in_past(df, rule)
            elif rule_type == "derived_consistency":
                issues += self._check_derived_consistency(df, rule)
            elif rule_type == "derived_range":
                issues += self._check_derived_range(df, rule)
            elif rule_type == "regex_optional":
                issues += self._check_regex(df, rule)

        issues_df = pd.DataFrame(issues)
        logging.info(f"PrecisionAgent: {len(issues_df)} issues detected.")
        return issues_df

    def _check_categorical(self, df: pd.DataFrame, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        col = rule["column"]
        allowed = set(str(a).lower() for a in rule.get("allowed", []))
        invalid_rows = df[~df[col].astype(str).str.lower().isin(allowed)]
        return [{"rule": rule["name"], "column": col, "row": i, "value": v}
                for i, v in invalid_rows[col].items()]

    def _check_range(self, df: pd.DataFrame, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        col = rule["column"]
        min_val, max_val = rule.get("min"), rule.get("max")
        mask = (df[col] < min_val) | (df[col] > max_val)
        return [{"rule": rule["name"], "column": col, "row": i, "value": v}
                for i, v in df.loc[mask, col].items()]

    def _check_nonnegative(self, df: pd.DataFrame, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        col = rule["column"]
        invalid_rows = df[df[col] < 0]
        return [{"rule": rule["name"], "column": col, "row": i, "value": v}
                for i, v in invalid_rows[col].items()]

    def _check_date_in_past(self, df: pd.DataFrame, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        from datetime import datetime
        col = rule["column"]
        now = datetime.now()
        invalid = df[pd.to_datetime(df[col], errors="coerce") > now]
        return [{"rule": rule["name"], "column": col, "row": i, "value": v}
                for i, v in invalid[col].items()]

    def _check_derived_consistency(self, df: pd.DataFrame, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        formula = rule["formula"]
        target = rule["target_column"]
        tolerance = rule.get("tolerance", 0.1)
        derived = df.eval(formula)
        diff = np.abs(df[target] - derived) / (derived + 1e-9)
        inconsistent = diff > tolerance
        return [{"rule": rule["name"], "column": target, "row": i, "value": df.loc[i, target]}
                for i in df.index[inconsistent]]

    def _check_derived_range(self, df: pd.DataFrame, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        from datetime import datetime
        col = rule["derived_from"]
        now = datetime.now()
        age = (now - pd.to_datetime(df[col], errors="coerce")).dt.days / 365.25
        mask = (age < rule["min"]) | (age > rule["max"])
        return [{"rule": rule["name"], "column": col, "row": i, "value": v}
                for i, v in df.loc[mask, col].items()]

    def _check_regex(self, df: pd.DataFrame, rule: Dict[str, Any]) -> List[Dict[str, Any]]:
        import re
        col = rule["column"]
        pattern = re.compile(rule["pattern"])
        invalid = df[~df[col].astype(str).str.match(pattern, na=True)]
        return [{"rule": rule["name"], "column": col, "row": i, "value": v}
                for i, v in invalid[col].items()]


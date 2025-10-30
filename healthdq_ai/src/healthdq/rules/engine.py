"""
engine.py — Datu kvalitātes noteikumu dzinējs (Data Quality Rule Engine)
=========================================================================

Šis modulis īsteno datu kvalitātes validācijas mehānismu veselības datu
prototipam *healthdq-ai*, kas ir daļa no promocijas darba
“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai
atvērtās zinātnes iniciatīvās”.

Mērķis:
--------
Interpretēt un izpildīt YAML formātā definētus datu kvalitātes noteikumus
(`rules.yml`), aptverot trīs pamatdimensijas:
  - **Precizitāte (Precision)** — loģiskā un formālā korektība;
  - **Pilnīgums (Completeness)** — prasīto kolonnu esamība;
  - **Atkārtota izmantojamība (Reusability)** — formātu, vienību un semantikas atbilstība.

Funkcionalitāte:
----------------
- Izpilda kategoriskos, diapazonu, datumu un regulāro izteiksmju noteikumus
- Ģenerē pārkāpumu (issues) atskaiti ar skaidriem ziņojumiem
- Saglabā FAIR reproducējamības metadatus (timestamp, rules_used, summary)

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

import re
import pandas as pd
from datetime import datetime


# ---------------------------------------------------------------------
# Pamata atskaites klase
# ---------------------------------------------------------------------
class DQReport:
    """
    DQReport apkopo visus datu kvalitātes pārkāpumus (“issues”),
    ko atklāj noteikumu dzinējs. Katrs pārkāpums satur:
      - rule: noteikuma nosaukumu (`rules.yml` sadaļā “name”)
      - row: datu rindas indeksu
      - message: paskaidrojumu par pārkāpumu
    """

    def __init__(self):
        self.issues = []
        self.meta = {
            "generated_at": datetime.now().isoformat(),
            "total_issues": 0,
            "rules_applied": [],
        }

    def add(self, rule_name, row_idx, msg):
        """Pievieno jaunu pārkāpumu ziņojumu."""
        self.issues.append({
            "rule": rule_name,
            "row": int(row_idx),
            "message": msg
        })

    def to_frame(self) -> pd.DataFrame:
        """Pārveido pārkāpumu sarakstu uz DataFrame reproducējamā formā."""
        df = (
            pd.DataFrame(self.issues)
            if self.issues
            else pd.DataFrame(columns=["rule", "row", "message"])
        )
        self.meta["total_issues"] = len(df)
        return df

    def summary(self) -> dict:
        """Atgriež metadatu kopsavilkumu reproducējamībai."""
        return self.meta


# ---------------------------------------------------------------------
# Galvenā funkcija: noteikumu interpretācija un izpilde
# ---------------------------------------------------------------------
def run_checks(df: pd.DataFrame, config: dict) -> DQReport:
    """
    Izpilda YAML konfigurācijā (`rules.yml`) definētos noteikumus un
    atgriež strukturētu pārkāpumu atskaiti (DQReport).

    Parametri:
    -----------
    df : pd.DataFrame
        Datu kopa, kas jāvalidē
    config : dict
        Ielādētā YAML konfigurācija ar “required_columns” un “rules” sadaļām

    Atgriež:
    --------
    DQReport objektu ar:
      - .issues: saraksts ar pārkāpumiem
      - .to_frame(): DataFrame formāts
      - .summary(): reproducējamības metadati
    """

    rep = DQReport()

    # 1. Obligāto kolonnu pārbaude
    for col in config.get("required_columns", []):
        if col not in df.columns:
            rep.add("required_columns", -1, f"❌ Missing required column: {col}")

    # 2. Galveno noteikumu izpilde
    rules = config.get("rules", [])
    rep.meta["rules_applied"] = [r.get("name") for r in rules]

    for i, row in df.iterrows():
        for rule in rules:
            rule_name = rule.get("name", "unnamed_rule")
            rule_type = rule.get("type")
            column = rule.get("column")

            if column not in df.columns:
                continue
            val = row[column]

            try:
                # --- Kategoriskie noteikumi ---
                if rule_type == "categorical":
                    allowed = set(rule.get("allowed", []))
                    if pd.notna(val) and val not in allowed:
                        rep.add(rule_name, i, f"{column}='{val}' not in {allowed}")

                # --- Datuma noteikumi ---
                elif rule_type == "date_in_past":
                    if pd.isna(val):
                        continue
                    try:
                        d = pd.to_datetime(val)
                        if d > pd.Timestamp.now():
                            rep.add(rule_name, i, f"{column}='{val}' is in the future")
                    except Exception:
                        rep.add(rule_name, i, f"{column}='{val}' not parseable as date")

                # --- Diapazona noteikumi ---
                elif rule_type == "range":
                    minv, maxv = rule.get("min"), rule.get("max")
                    if pd.notna(val) and not (minv <= float(val) <= maxv):
                        rep.add(rule_name, i, f"{column}={val} not in [{minv},{maxv}]")

                # --- Negatīvo vērtību pārbaude ---
                elif rule_type == "nonnegative":
                    if pd.notna(val) and float(val) < 0:
                        rep.add(rule_name, i, f"{column}='{val}' is negative")

                # --- Regex validācija ---
                elif rule_type == "regex_optional":
                    pattern = re.compile(rule.get("pattern", ""))
                    if pd.notna(val) and not pattern.match(str(val)):
                        rep.add(rule_name, i, f"{column}='{val}' does not match pattern {pattern.pattern}")

                # --- Atvasinātas loģikas noteikums (piemēram, BMI) ---
                elif rule_type == "derived_consistency":
                    formula = rule.get("formula")
                    target_col = rule.get("target_column")
                    tol = rule.get("tolerance", 0.25)
                    try:
                        if pd.notna(val):
                            # Izpilda formulu drošā kontekstā
                            derived = eval(formula, {}, dict(row))
                            if not (abs(derived - val) / val <= tol):
                                rep.add(rule_name, i, f"{column}={val} inconsistent with derived {round(derived, 2)}")
                    except Exception as e:
                        rep.add(rule_name, i, f"❌ Error evaluating formula {formula}: {e}")

            except Exception as e:
                rep.add(rule_name, i, f"❌ Unexpected error while evaluating rule: {e}")

    return rep


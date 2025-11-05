"""
rule_validation.py — Human-in-the-Loop (HITL) validācijas modulis
==================================================================

Šis modulis ļauj validēt AI ģenerētos datu kvalitātes noteikumus, 
pārbaudot to piemērotību datu kopai un ļaujot cilvēkam tos apstiprināt vai noraidīt.

Tas ir daļa no reproducējamas, cilvēka vadītas datu kvalitātes pārvaldības plūsmas.
"""

import yaml
import pandas as pd
import json
from pathlib import Path
from datetime import datetime


class RuleValidator:
    """
    RuleValidator — pārbauda, cik labi AI ģenerētie noteikumi atbilst reālajiem datiem.
    Ļauj cilvēkam (HITL) apstiprināt vai noraidīt šos noteikumus.
    """

    def __init__(self, rules_path="out/rules_generated.yml", output_dir="out"):
        self.rules_path = Path(rules_path)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.rules = self._load_rules()

    def _load_rules(self):
        """Ielādē YAML noteikumu konfigurāciju."""
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Noteikumu fails nav atrasts: {self.rules_path}")
        with open(self.rules_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def validate_rules(self, df: pd.DataFrame, confidence_threshold: float = 0.7) -> pd.DataFrame:
        """
        Pārbauda katra noteikuma atbilstību datu kopai.
        Aprēķina 'confidence' (uzticamību) un 'coverage' (pielietojamību).
        """
        validation_results = []

        for rule in self.rules.get("rules", []):
            col = rule.get("column")
            if col not in df.columns:
                validation_results.append({
                    "rule_name": rule.get("name"),
                    "type": rule.get("type"),
                    "column": col,
                    "dimension": rule.get("dimension", "unknown"),
                    "status": "missing_column",
                    "confidence": 0.0,
                    "coverage": 0.0
                })
                continue

            try:
                series = df[col]
                status, confidence, coverage = self._apply_rule(series, rule)
            except Exception:
                status, confidence, coverage = "error", 0.0, 0.0

            validation_results.append({
                "rule_name": rule.get("name"),
                "type": rule.get("type"),
                "column": col,
                "dimension": rule.get("dimension", "unknown"),
                "status": status,
                "confidence": round(confidence, 3),
                "coverage": round(coverage, 3)
            })

        self.validation_table = pd.DataFrame(validation_results)
        self.low_confidence = self.validation_table[self.validation_table["confidence"] < confidence_threshold]
        return self.validation_table

    def _apply_rule(self, series: pd.Series, rule: dict):
        """Izpilda noteikuma pārbaudi uz dotās kolonnas."""
        if series.isna().all():
            return "no_data", 0.0, 0.0

        rule_type = rule.get("type", "unknown")
        if rule_type == "range":
            valid = series.between(rule.get("min", -float("inf")), rule.get("max", float("inf")))
        elif rule_type == "categorical":
            valid = series.isin(rule.get("allowed", []))
        elif rule_type == "date_range":
            series = pd.to_datetime(series, errors="coerce")
            valid = series.between(rule.get("min"), rule.get("max"))
        elif rule_type == "completeness":
            valid = ~series.isna()
        else:
            return "unsupported_rule", 0.0, 0.0

        coverage = valid.mean()
        return "ok", coverage, coverage

    def save_validation_results(self):
        """Saglabā validācijas rezultātus CSV un JSON formātos."""
        if not hasattr(self, "validation_table"):
            raise RuntimeError("Vispirms jāizsauc validate_rules() metode.")
        csv_path = self.output_dir / "rule_validation_results.csv"
        json_path = self.output_dir / "rule_validation_results.json"
        self.validation_table.to_csv(csv_path, index=False)
        self.validation_table.to_json(json_path, orient="records", indent=2)
        return csv_path, json_path

    def get_rules_for_review(self) -> pd.DataFrame:
        """Atgriež noteikumus, kuriem nepieciešama cilvēka validācija."""
        if not hasattr(self, "low_confidence"):
            raise RuntimeError("Vispirms jāizpilda validate_rules().")
        return self.low_confidence

    def save_validated_rules(self, human_feedback: pd.DataFrame):
        """
        Saglabā gala validēto YAML konfigurāciju, apvienojot cilvēka atsauksmes.
        """
        validated_yaml = self.rules.copy()
        validated_yaml["metadata"]["validated_at"] = datetime.now().isoformat()
        validated_yaml["metadata"]["validated_by"] = "Human-in-the-Loop"
        validated_yaml["metadata"]["reviewed_rules"] = len(human_feedback)

        for idx, row in human_feedback.iterrows():
            rule_name = row["rule_name"]
            decision = row.get("decision", "accept")
            for r in validated_yaml.get("rules", []):
                if r.get("name") == rule_name:
                    r["human_validation"] = decision

        out_file = self.output_dir / "rules_validated.yml"
        with open(out_file, "w", encoding="utf-8") as f:
            yaml.safe_dump(validated_yaml, f, sort_keys=False, allow_unicode=True)
        return out_file


if __name__ == "__main__":
    import pandas as pd

    # Testēšana ar piemēra datiem
    sample_path = Path("data/sample/500_dati_testiem.csv")
    if sample_path.exists():
        df = pd.read_csv(sample_path)
        validator = RuleValidator()
        table = validator.validate_rules(df)
        validator.save_validation_results()
        print("Automātiskā validācija pabeigta.")
        print(validator.get_rules_for_review().head())

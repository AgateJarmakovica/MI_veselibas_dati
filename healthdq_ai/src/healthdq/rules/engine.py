import re, pandas as pd
from datetime import datetime

class DQReport:
    def __init__(self): self.issues = []
    def add(self, rule_name, row_idx, msg): self.issues.append({"rule": rule_name, "row": int(row_idx), "message": msg})
    def to_frame(self): return pd.DataFrame(self.issues) if self.issues else pd.DataFrame(columns=["rule","row","message"])

def run_checks(df: pd.DataFrame, config: dict) -> DQReport:
    rep = DQReport()
    for col in config.get("required_columns", []):
        if col not in df.columns: rep.add("required_columns",-1,f"Missing required column: {col}")
    rules = config.get("rules", [])
    for i, row in df.iterrows():
        for rule in rules:
            rtype, col = rule["type"], rule["column"]
            if col not in df.columns: continue
            val = row[col]
            if rtype == "categorical":
                allowed = set(rule.get("allowed", []))
                if pd.notna(val) and val not in allowed: rep.add(rule["name"], i, f"{col}='{val}' not in {allowed}")
            elif rtype == "date_in_past":
                try:
                    if pd.isna(val): continue
                    d = pd.to_datetime(val)
                    if d > pd.Timestamp.now(): rep.add(rule["name"], i, f"{col}='{val}' is in the future")
                except Exception: rep.add(rule["name"], i, f"{col}='{val}' not parseable as date")
            elif rtype == "nonnegative":
                if pd.notna(val) and float(val) < 0: rep.add(rule["name"], i, f"{col}='{val}' is negative")
            elif rtype == "range":
                minv, maxv = rule.get("min"), rule.get("max")
                if pd.notna(val) and not (minv <= float(val) <= maxv): rep.add(rule["name"], i, f"{col}={val} not in [{minv},{maxv}]")
            elif rtype == "regex_optional":
                patt = re.compile(rule.get("pattern",""))
                if pd.notna(val) and not patt.match(str(val)): rep.add(rule["name"], i, f"{col}='{val}' does not match pattern {patt.pattern}")
    return rep

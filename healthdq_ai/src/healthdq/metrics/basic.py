import pandas as pd

def not_null_rate(df: pd.DataFrame, columns):
    return {c: float(df[c].notna().mean()) if c in df.columns else None for c in columns}

def out_of_range_rate(df: pd.DataFrame, columns):
    # placeholder: would leverage rules to know ranges; here, simply count negatives for demo of BMI/values
    res = {}
    for c in columns:
        if c in df.columns:
            s = df[c].dropna().astype(float)
            res[c] = float((s<0).mean())
        else:
            res[c] = None
    return res

def compute_metrics(df_before: pd.DataFrame, df_after: pd.DataFrame, config: dict):
    out = {"before":{}, "after":{}}
    for m in config.get("metrics", []):
        if m["type"] == "not_null_rate":
            out["before"][m["name"]] = not_null_rate(df_before, m["columns"])
            out["after"][m["name"]]  = not_null_rate(df_after,  m["columns"])
        elif m["type"] == "out_of_range_rate":
            out["before"][m["name"]] = out_of_range_rate(df_before, m["columns"])
            out["after"][m["name"]]  = out_of_range_rate(df_after,  m["columns"])
    return out

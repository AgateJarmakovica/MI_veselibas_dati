import json, pandas as pd
def load_json_records(path: str) -> pd.DataFrame:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return pd.json_normalize(data)

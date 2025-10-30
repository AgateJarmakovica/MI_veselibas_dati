import pandas as pd

def harmonize_semantics(df: pd.DataFrame, semantic_maps: dict) -> pd.DataFrame:
    df = df.copy()
    for col, mapping in semantic_maps.items():
        if col in df.columns:
            df[col] = df[col].map(mapping).fillna(df[col])
    return df

def compute_bmi(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "bmi" in df.columns and "height_cm" in df.columns and "weight_kg" in df.columns:
        need = df["bmi"].isna() & df["height_cm"].notna() & df["weight_kg"].notna()
        df.loc[need, "bmi"] = (df.loc[need, "weight_kg"] / (df.loc[need, "height_cm"]/100)**2).round(2)
    return df

def impute_simple(df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    df = df.copy()
    for col, strat in strategy.items():
        if col not in df.columns: continue
        if strat == "median":
            val = df[col].median(skipna=True); df[col] = df[col].fillna(val)
        elif strat == "mode":
            val = df[col].mode(dropna=True); val = val.iloc[0] if len(val)>0 else None; df[col] = df[col].fillna(val)
        elif strat == "compute_from_height_weight":
            df = compute_bmi(df)
    return df

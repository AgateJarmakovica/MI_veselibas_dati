import pandas as pd
from ..rules import impute_simple

class CompletenessAgent:
    def __init__(self, config): self.config = config
    def run(self, df: pd.DataFrame):
        # apply imputations (median/mode/BMI) to address missingness
        df_imp = impute_simple(df, self.config.get("imputation", {}).get("strategy", {}))
        return df_imp

import pandas as pd
from ..rules import harmonize_semantics

class ReusabilityAgent:
    def __init__(self, config): self.config = config
    def run(self, df: pd.DataFrame):
        # semantic harmonization (e.g., female/male -> F/M)
        df_sem = harmonize_semantics(df, self.config.get("semantic_maps", {}))
        return df_sem

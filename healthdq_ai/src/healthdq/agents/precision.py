import pandas as pd
from ..rules import run_checks

class PrecisionAgent:
    def __init__(self, config): self.config = config
    def run(self, df: pd.DataFrame):
        # run_checks already contains ranges/regex/dates—precision focused
        rep = run_checks(df, self.config)
        return rep.to_frame()

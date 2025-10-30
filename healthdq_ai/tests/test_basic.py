import pandas as pd
from healthdq.rules import compute_bmi

def test_bmi():
    df = pd.DataFrame({'height_cm':[180],'weight_kg':[81],'bmi':[None]})
    out = compute_bmi(df)
    assert round(out.loc[0,'bmi'],2) == 25.0

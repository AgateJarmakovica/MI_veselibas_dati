import pandas as pd
from healthdq.rules.transform import compute_bmi, harmonize_semantics, impute_simple


def test_bmi():
    df = pd.DataFrame({'height_cm': [180], 'weight_kg': [81], 'bmi': [None]})
    out = compute_bmi(df)
    assert round(out.loc[0, 'bmi'], 2) == 25.0


def test_semantic_harmonization():
    df = pd.DataFrame({'sex_at_birth': ['female', 'Male', 'm']})
    mapping = {'sex_at_birth': {'female': 'F', 'Male': 'M', 'm': 'M'}}
    out = harmonize_semantics(df, mapping)
    assert set(out['sex_at_birth'].unique()) == {'F', 'M'}


def test_imputation_median():
    df = pd.DataFrame({'height_cm': [150, 160, None, 170]})
    strategy = {'height_cm': 'median'}
    out = impute_simple(df, strategy)
    assert out['height_cm'].isna().sum() == 0
    assert out['height_cm'].median() == 160

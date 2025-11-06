import pandas as pd
import pytest

from healthdq.rules.transform import compute_bmi, harmonize_semantics, impute_simple


def test_compute_bmi_missing_column():
    df = pd.DataFrame({"weight_kg": [80]})
    with pytest.raises(KeyError):
        compute_bmi(df)


def test_harmonize_semantics_unknown_column():
    df = pd.DataFrame({"sex": ["F"]})
    with pytest.raises(KeyError):
        harmonize_semantics(df, {"sex_at_birth": {"F": "Female"}})


def test_impute_simple_requires_constant_value():
    df = pd.DataFrame({"status": [None, "ok"]})
    with pytest.raises(ValueError):
        impute_simple(df, {"status": "constant"})

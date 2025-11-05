"""
rule_learning.py — Vispārīgs pašmācības modulis datu struktūru izpratnei un kvalitātes noteikumu atklāšanai
============================================================================================================

Šī versija nav piesaistīta nevienai domēna struktūrai. Tā izmanto adaptīvu semantisko modelēšanu,
lai iemācītos datu struktūras, nozīmes un atkarības neatkarīgi no datu veida.

Metodes:
---------
1. Statistiskā analīze — nosaka kolonnas tipu, vērtību sadalījumu un korelācijas.
2. Semantiskā atklāšana — vektorizē kolonu nosaukumus un biežākās vērtības, veidojot datu "jēdzienisko karti".
3. Noteikumu ģenerācija — izveido automātiskus kandidātus (range, pattern, correlation, categorical).
4. Pašmācība — veido ontoloģiju no datu kopas, kas tiek izmantota nākotnes datu interpretācijai.
"""

import pandas as pd
import numpy as np
import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path


class UniversalSchemaLearner:
    def __init__(self, ontology_store="out/learned_ontology.json"):
        self.ontology_store = Path(ontology_store)
        self.vectorizer = TfidfVectorizer()
        self.learned_ontology = self._load_existing_ontology()

    def _load_existing_ontology(self):
        if self.ontology_store.exists():
            with open(self.ontology_store, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"terms": [], "embeddings": []}

    def fit(self, df: pd.DataFrame):
        schema_info = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            summary = self._analyze_column(df[col])
            schema_info.append({"column": col, "dtype": dtype, "summary": summary})
        self.schema_info = schema_info
        return self

    # ---------------------------------------------------------------
    # Kolonnu analīze pēc datu tipa un sadalījuma
    # ---------------------------------------------------------------
    def _analyze_column(self, series: pd.Series):
        if pd.api.types.is_numeric_dtype(series):
            return {
                "min": float(series.min(skipna=True)),
                "max": float(series.max(skipna=True)),
                "mean": float(series.mean(skipna=True)),
                "std": float(series.std(skipna=True)),
                "missing": int(series.isna().sum()),
            }
        elif pd.api.types.is_datetime64_any_dtype(series):
            return {
                "min_date": str(series.min(skipna=True)),
                "max_date": str(series.max(skipna=True)),
                "missing": int(series.isna().sum()),
            }
        else:
            values = series.dropna().astype(str)
            freq = values.value_counts().head(5).to_dict()
            pattern = self._detect_pattern(values)
            return {"most_common": list(freq.keys()), "pattern": pattern, "missing": int(series.isna().sum())}

    # ---------------------------------------------------------------
    # Atpazīst regulāras struktūras (piem., ID, kodus, datumu formātus)
    # ---------------------------------------------------------------
    def _detect_pattern(self, values):
        sample = " ".join(values.sample(min(100, len(values)))).lower()
        if re.search(r"\d{4}-\d{2}-\d{2}", sample):
            return "date_format"
        if re.search(r"^[a-z]{2,}[0-9]+", sample):
            return "code_mixed"
        if re.search(r"^[A-Z0-9\-]+$", sample):
            return "alphanumeric_code"
        return "free_text"

    # ---------------------------------------------------------------
    # Veido semantisku ontoloģiju no pašas datu kopas
    # ---------------------------------------------------------------
    def learn_semantics(self, df: pd.DataFrame):
        # Ņem vērā kolonnu nosaukumus un biežākās vērtības
        terms = list(df.columns)
        values = []
        for col in df.columns:
            most_common = df[col].dropna().astype(str).value_counts().head(3).index.tolist()
            values.extend(most_common)

        combined_terms = list(set(terms + values))
        X = self.vectorizer.fit_transform(combined_terms)
        embeddings = X.toarray().tolist()
        self.learned_ontology = {"terms": combined_terms, "embeddings": embeddings}
        return self.learned_ontology

    # ---------------------------------------------------------------
    # Automātiska noteikumu ģenerēšana
    # ---------------------------------------------------------------
    def generate_rules(self, df: pd.DataFrame, correlation_threshold=0.7):
        rules = []
        # Skaitliskās korelācijas
        numeric_df = df.select_dtypes(include=["float", "int"])
        if not numeric_df.empty:
            corr = numeric_df.corr()
            for c1 in corr.columns:
                for c2 in corr.columns:
                    if c1 != c2 and corr.loc[c1, c2] >= correlation_threshold:
                        rules.append({
                            "type": "correlation",
                            "columns": [c1, c2],
                            "correlation": float(corr.loc[c1, c2]),
                        })

        # Skaitliskās robežas un kategorijas
        for col in df.columns:
            dtype = str(df[col].dtype)
            if "float" in dtype or "int" in dtype:
                rules.append({
                    "type": "range",
                    "column": col,
                    "min": float(df[col].min(skipna=True)),
                    "max": float(df[col].max(skipna=True))
                })
            elif "object" in dtype:
                allowed = df[col].dropna().unique().tolist()[:10]
                rules.append({"type": "categorical", "column": col, "allowed": allowed})
        return rules

    # ---------------------------------------------------------------
    # Saglabā ontoloģiju un noteikumus
    # ---------------------------------------------------------------
    def save(self, out_dir="out"):
        Path(out_dir).mkdir(parents=True, exist_ok=True)
        with open(f"{out_dir}/ontology.json", "w", encoding="utf-8") as f:
            json.dump(self.learned_ontology, f, indent=2, ensure_ascii=False)
        with open(f"{out_dir}/rules_generated.json", "w", encoding="utf-8") as f:
            json.dump(self.schema_info, f, indent=2, ensure_ascii=False)


# ------------------------------------------------------------------
# Palīgfunkcija pipeline integrācijai
# ------------------------------------------------------------------
def learn_rules_from_any_data(df: pd.DataFrame, out_dir="out"):
    learner = UniversalSchemaLearner()
    learner.fit(df)
    learner.learn_semantics(df)
    rules = learner.generate_rules(df)
    learner.save(out_dir)
    return rules

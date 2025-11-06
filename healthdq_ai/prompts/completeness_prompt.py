import json
import pandas as pd
from .base_prompt import BasePromptGenerator


class CompletenessPromptGenerator(BasePromptGenerator):
    """
    Dinamisks promptu ģenerators pilnīguma (Completeness) dimensijai.
    Šis modulis analizē datu struktūru un sagatavo MI kontekstu
    trūkstošo vērtību identificēšanai un aizpildīšanas stratēģijai.
    """

    def __init__(self, dataset_name: str, rules: dict, context: dict = None):
        super().__init__(dataset_name, rules, context)

    def detect_missing_patterns(self, df: pd.DataFrame) -> dict:
        """
        Analizē trūkstošo vērtību sadalījumu un korelācijas starp kolonnām.
        """
        missing_summary = df.isnull().sum().to_dict()
        missing_ratio = df.isnull().mean().round(3).to_dict()
        correlated_missing = {}

        # Korelētās trūkstošās vērtības — ja divas kolonnas bieži tukšas kopā
        for col in df.columns:
            for other in df.columns:
                if col != other:
                    both_missing = ((df[col].isnull()) & (df[other].isnull())).mean()
                    if both_missing > 0.2:
                        correlated_missing[(col, other)] = round(float(both_missing), 3)

        return {
            "missing_counts": missing_summary,
            "missing_ratios": missing_ratio,
            "correlated_missing": correlated_missing
        }

    def recommend_imputation_strategies(self, df: pd.DataFrame) -> dict:
        """
        Piedāvā ieteicamas aizpildīšanas (imputation) metodes pēc datu tipa un sadalījuma.
        """
        strategies = {}
        for col in df.columns:
            dtype = str(df[col].dtype)
            null_ratio = df[col].isnull().mean()

            if null_ratio == 0:
                continue

            if "float" in dtype or "int" in dtype:
                strategies[col] = "median" if null_ratio < 0.3 else "predictive (AI)"
            elif "object" in dtype:
                strategies[col] = "mode"
            elif "datetime" in dtype:
                strategies[col] = "interpolate"
            else:
                strategies[col] = "auto"

        return strategies

    def generate_completeness_prompt(self, df: pd.DataFrame) -> str:
        """
        Izveido dinamisku promptu MI modelim pilnīguma uzlabošanai.
        """
        structure_info = self.analyze_structure(df)
        missing_info = self.detect_missing_patterns(df)
        impute_suggestions = self.recommend_imputation_strategies(df)
        context_text = json.dumps(self.context, indent=2, ensure_ascii=False)
        rule_summary = ", ".join(self.rules.get("imputation", {}).keys()) or "Nav definētu noteikumu"

        prompt = f"""
        Tu esi MI aģents, kas analizē datu pilnīgumu (Completeness Dimension).

        Datu kopa: {self.dataset_name}
        Kolonnas: {structure_info['columns']}
        Datu tipi: {json.dumps(structure_info['types'], ensure_ascii=False)}
        Trūkstošo vērtību īpatsvars: {json.dumps(structure_info['null_rates'], ensure_ascii=False)}
        Trūkstošo vērtību struktūra: {json.dumps(missing_info, ensure_ascii=False, indent=2)}

        Ieteicamās imputācijas metodes pēc tipa: {json.dumps(impute_suggestions, ensure_ascii=False, indent=2)}

        Lietotāja konteksts: {context_text}
        Aktīvie noteikumi: {rule_summary}

        Tava uzvedība:
        - Atpazīsti kolonnas ar augstu trūkstošo vērtību īpatsvaru (>20%).
        - Iesaki piemērotu imputācijas stratēģiju (median, mode, interpolation, predictive).
        - Ja datu struktūra nav zināma, analizē vērtību sadalījumu, lai noteiktu iespējamos tipus.
        - Pārbaudi, vai trūkstošie dati korelē starp kolonnām (piem., height un weight kopā).
        - Piedāvā ieteikumus cilvēka apstiprināšanai (HITL), lai validētu imputācijas rezultātus.
        """
        return prompt.strip()

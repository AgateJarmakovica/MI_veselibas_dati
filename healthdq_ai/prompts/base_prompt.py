import json
import pandas as pd

class BasePromptGenerator:
    """Dinamiska promptu ģenerēšanas sistēma aģentiem."""

    def __init__(self, dataset_name: str, rules: dict, context: dict = None):
        self.dataset_name = dataset_name
        self.rules = rules
        self.context = context or {}

    def analyze_structure(self, df: pd.DataFrame) -> dict:
        """Automātiski analizē datu struktūru, lai pielāgotu promptu."""
        summary = {
            "columns": df.columns.tolist(),
            "types": df.dtypes.apply(lambda x: str(x)).to_dict(),
            "null_rates": df.isnull().mean().round(3).to_dict(),
            "shape": df.shape
        }
        return summary

    def generate_prompt(self, df: pd.DataFrame, dimension: str) -> str:
        """Ģenerē pielāgotu promptu konkrētai dimensijai."""
        structure_info = self.analyze_structure(df)
        context_text = json.dumps(self.context, indent=2, ensure_ascii=False)
        rule_summary = ", ".join([r["name"] for r in self.rules.get("rules", [])])

        return f"""
        Tu esi MI aģents, kas novērtē datu kvalitāti dimensijā: {dimension}.
        Datu kopa: {self.dataset_name}
        Kolonnas: {structure_info['columns']}
        Tips: {structure_info['types']}
        Trūkstošo datu īpatsvars: {structure_info['null_rates']}
        Lietotāja konteksts: {context_text}
        Aktīvie noteikumi: {rule_summary}

        Tava loma:
        - Atpazīt kļūdas un anomālijas (pat ja kolonnu nosaukumi nav zināmi iepriekš).
        - Ierosināt loģiskus uzlabojumus, izmantojot datu struktūras un semantikas līdzību.
        - Nodrošināt pārskatāmu ieteikumu, ko var pārbaudīt lietotājs.
        """

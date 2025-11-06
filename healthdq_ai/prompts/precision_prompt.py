import json
import pandas as pd
from .base_prompt import BasePromptGenerator


class PrecisionPromptGenerator(BasePromptGenerator):
    """
    Dinamisks promptu ģenerators precizitātes (Precision) dimensijai.
    Izmanto datu struktūru un noteikumus, lai formulētu MI uzvedības kontekstu.
    """

    def __init__(self, dataset_name: str, rules: dict, context: dict = None):
        super().__init__(dataset_name, rules, context)

    def detect_inconsistencies(self, df: pd.DataFrame) -> dict:
        """
        Automātiski identificē iespējamos loģiskos pārkāpumus (outliers, 
        neatbilstības, negatīvas vērtības u.c.), pat ja kolonnas nav zināmas iepriekš.
        """
        insights = {}
        for col in df.select_dtypes(include=["number"]).columns:
            col_data = df[col].dropna()
            if not col_data.empty:
                min_val, max_val = col_data.min(), col_data.max()
                mean_val, std_val = col_data.mean(), col_data.std()
                anomalies = ((col_data < mean_val - 3 * std_val) | (col_data > mean_val + 3 * std_val)).sum()
                if anomalies > 0:
                    insights[col] = {
                        "mean": round(mean_val, 3),
                        "std": round(std_val, 3),
                        "min": round(min_val, 3),
                        "max": round(max_val, 3),
                        "outliers": int(anomalies),
                    }
        return insights

    def generate_precision_prompt(self, df: pd.DataFrame) -> str:
        """
        Izveido detalizētu promptu, kas palīdz MI saprast un analizēt datu precizitāti.
        """
        structure_info = self.analyze_structure(df)
        inconsistencies = self.detect_inconsistencies(df)
        context_text = json.dumps(self.context, indent=2, ensure_ascii=False)
        rule_names = ", ".join([r["name"] for r in self.rules.get("rules", [])]) or "Nav noteikumu"

        prompt = f"""
        Tu esi datu kvalitātes MI aģents (PrecisionAgent),
        kura mērķis ir novērtēt un uzlabot veselības datu loģisko un semantisko korektumu.

        Datu kopa: {self.dataset_name}
        Kolonnas: {structure_info['columns']}
        Tipi: {json.dumps(structure_info['types'], ensure_ascii=False)}
        Trūkstošo vērtību īpatsvars: {json.dumps(structure_info['null_rates'], ensure_ascii=False)}
        Atrastās iespējamās neatbilstības: {json.dumps(inconsistencies, ensure_ascii=False, indent=2)}

        Aktīvie noteikumi: {rule_names}
        Lietotāja konteksts: {context_text}

        Tava uzvedība:
        - Identificē neparastas vai loģiski neiespējamas vērtības (piemēram, negatīvs svars, dzimšanas datums nākotnē).
        - Ja kolonnu nozīmes nav zināmas, mēģini tās interpretēt pēc nosaukuma vai vērtību rakstura.
        - Pārbaudi iekšējo konsekvenci starp kolonnām (piemēram, svars ↔ augums ↔ BMI).
        - Sagatavo pārskatāmu atskaiti ar kļūdu aprakstu un ticamības pakāpi.
        - Piedāvā ieteikumus, kā uzlabot datu kvalitāti (piemēram, pārrēķināt BMI vai normalizēt vērtības).
        """
        return prompt.strip()

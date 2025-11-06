import json
import pandas as pd
from difflib import SequenceMatcher
from .base_prompt import BasePromptGenerator

try:
    from sentence_transformers import SentenceTransformer, util
    _SEM_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
except Exception:
    _SEM_MODEL = None


class ReusabilityPromptGenerator(BasePromptGenerator):
    """
    Dinamisks promptu ģenerators atkārtotas izmantojamības (Reusability) dimensijai.
    Šis modulis analizē jebkuru datu struktūru, pat ja lauku nosaukumi vai nozīmes nav zināmas.
    Tas atrod semantiskās līdzības, terminoloģiskās atbilstības un piedāvā harmonizācijas kartes.
    """

    def __init__(self, dataset_name: str, rules: dict, context: dict = None):
        super().__init__(dataset_name, rules, context)

    def semantic_similarity(self, a: str, b: str) -> float:
        """Aprēķina semantisko līdzību starp diviem jēdzieniem."""
        if _SEM_MODEL:
            emb_a = _SEM_MODEL.encode(a, convert_to_tensor=True)
            emb_b = _SEM_MODEL.encode(b, convert_to_tensor=True)
            return float(util.cos_sim(emb_a, emb_b))
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def discover_column_semantics(self, df: pd.DataFrame) -> dict:
        """Atpazīst kolonnu nozīmes pēc nosaukuma, datu tipa un vērtībām."""
        discovered = {}
        for col in df.columns:
            sample_vals = df[col].dropna().astype(str).head(10).tolist()
            dtype = str(df[col].dtype)
            null_rate = round(df[col].isnull().mean(), 3)

            hints = []
            col_l = col.lower()
            if any(x in col_l for x in ["id", "uuid", "record"]):
                hints.append("identifikators")
            if any(x in col_l for x in ["date", "time", "birth"]):
                hints.append("datums / laiks")
            if any(x in col_l for x in ["name", "label", "desc"]):
                hints.append("teksts / nosaukums")
            if any(x in col_l for x in ["sex", "gender"]):
                hints.append("dzimums / kategorija")
            if any(x in col_l for x in ["height", "length", "cm"]):
                hints.append("augums / mērījums")
            if any(x in col_l for x in ["weight", "mass", "kg"]):
                hints.append("svars / mērījums")
            if any(x in col_l for x in ["code", "icd", "loinc"]):
                hints.append("medicīniskais kods")

            discovered[col] = {
                "dtype": dtype,
                "null_rate": null_rate,
                "examples": sample_vals,
                "semantic_hints": hints or ["nezināms"],
            }
        return discovered

    def auto_match_to_standards(self, df: pd.DataFrame) -> dict:
        """
        Mēģina automātiski saskaņot kolonnas ar zināmiem konceptiem.
        Der jebkurai datu kopai — ne tikai veselības.
        """
        standards = {
            "id": ["id", "uuid", "record_id"],
            "name": ["name", "title", "label"],
            "date": ["date", "timestamp", "datetime"],
            "value": ["value", "amount", "score", "measurement"],
            "category": ["type", "class", "group", "category"],
        }

        mappings = {}
        for col in df.columns:
            best_match, best_score = None, 0
            for std, aliases in standards.items():
                for alias in aliases:
                    score = self.semantic_similarity(col, alias)
                    if score > best_score:
                        best_match, best_score = std, score
            if best_score > 0.65:
                mappings[col] = {"mapped_to": best_match, "confidence": round(best_score, 3)}
        return mappings

    def generate_reusability_prompt(self, df: pd.DataFrame) -> str:
        """Izveido dinamisku promptu MI modelim atkārtotas izmantojamības analīzei."""
        structure_info = self.analyze_structure(df)
        semantic_analysis = self.discover_column_semantics(df)
        auto_mapping = self.auto_match_to_standards(df)
        rule_summary = ", ".join(self.rules.get("semantic_maps", {}).keys()) or "nav definētu noteikumu"
        context_text = json.dumps(self.context or {}, indent=2, ensure_ascii=False)

        prompt = f"""
Tu esi mākslīgā intelekta aģents, kura uzdevums ir analizēt datu atkārtotas izmantojamības (Reusability) aspektus.

1. Datu kopa: {self.dataset_name}
2. Kolonnas: {structure_info['columns']}
3. Datu tipi: {json.dumps(structure_info['types'], ensure_ascii=False)}
4. Null vērtību īpatsvars: {json.dumps(structure_info['null_rates'], ensure_ascii=False)}
5. Semantiskā analīze:
{json.dumps(semantic_analysis, indent=2, ensure_ascii=False)}
6. Automātiskie kartējumi:
{json.dumps(auto_mapping, indent=2, ensure_ascii=False)}

Noteikumi konfigurācijā: {rule_summary}
Papildu konteksts: {context_text}

Uzdevums:
- Identificē jēdzieniski līdzīgas kolonnas (pat ja to nosaukumi ir atšķirīgi).
- Piedāvā semantiski harmonizētu kolonnu nosaukumu kopumu.
- Sniedz priekšlikumus datu standartizācijai (piemēram, SNOMED, LOINC, ISO terminoloģijai).
- Ierosini, kā šie dati varētu tikt padarīti atkārtoti izmantojami (FAIR principi).
"""
        return prompt.strip()

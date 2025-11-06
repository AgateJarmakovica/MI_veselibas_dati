# =====================================================================
# schema_learner.py — Data Quality Schema Learning Component
# ---------------------------------------------------------------------
# Autore: Agate Jarmakoviča
# Versija: 1.3
# Datums: 2025-10-30
# ---------------------------------------------------------------------
# Mērķis:
#   Automātiski atpazīt kolonnu semantiku veselības datos,
#   lai ļautu modelim pielāgot noteikumus un kvalitātes pārbaudes
#   dažādām datu struktūrām.
#
# Šis komponents izmanto "sentence-transformers" modeli, lai
# salīdzinātu kolonnu nosaukumus ar iepriekš definētām semantiskām lomām.
# =====================================================================

import pandas as pd
import numpy as np
import json
import os

try:  # pragma: no cover - ārēja atkarība nav obligāta testos
    from sentence_transformers import SentenceTransformer, util
except ImportError:  # pragma: no cover
    SentenceTransformer = None
    util = None

class SchemaLearner:
    def __init__(self, model_name="sentence-transformers/paraphrase-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = SentenceTransformer(model_name) if SentenceTransformer else None

    def infer_roles(self, df: pd.DataFrame, predefined_roles=None):
        """Nosaka katras kolonnas iespējamo nozīmi (semantisko lomu)."""
        if predefined_roles is None:
            predefined_roles = [
                "patient_id", "birth_date", "sex_at_birth", 
                "height_cm", "weight_kg", "bmi", "icd10_code"
            ]

        col_names = df.columns.tolist()

        if self.model is None or util is None:
            mapping = {}
            for col in col_names:
                col_norm = col.lower()
                best = next((role for role in predefined_roles if role in col_norm), "unknown")
                confidence = 1.0 if best != "unknown" else 0.3
                mapping[col] = {"predicted_role": best, "confidence": round(confidence, 3)}
            return mapping

        column_embeddings = self.model.encode(col_names, convert_to_tensor=True)
        role_embeddings = self.model.encode(predefined_roles, convert_to_tensor=True)
        similarities = util.cos_sim(column_embeddings, role_embeddings)

        mapping = {}
        for i, col in enumerate(col_names):
            best_match_idx = int(np.argmax(similarities[i]))
            score = float(similarities[i][best_match_idx])
            mapping[col] = {"predicted_role": predefined_roles[best_match_idx], "confidence": round(score, 3)}

        return mapping

    def save_results(self, mapping, output_path="out/ai_learned_schema.json"):
        """Saglabā mācīšanās rezultātus JSON formātā."""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        return output_path

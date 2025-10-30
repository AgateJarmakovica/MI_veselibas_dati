"""
PrecisionAgent
===============

Šis modulis īsteno datu kvalitātes pārbaudi **precizitātes dimensijā (Precision)**,
kas ir viena no trim promocijas darba "healthdq-ai" pamatdimensijām.

Mērķis:
--------
Nodrošināt veselības datu loģisko un semantisko korektumu, izmantojot
noteikumu (`rules.yml`) pārbaudes mehānismus — diapazonus, regulārās izteiksmes,
datumu validāciju un atvasināto laukumu konsekvenci (piemēram, BMI aprēķins).

Šī pieeja balstīta uz Data-Centric AI un FAIR principiem:
- fokusējas uz datu precizitāti, nevis modeļu precizitāti;
- nodrošina pārskatāmību un reproducējamību;
- ļauj cilvēkam (HITL) pārskatīt anomālijas.

Autore: Agate Jarmakoviča
Versija: 1.2
Datums: 2025-10-30
"""

import pandas as pd
import datetime
from ..rules import run_checks


class PrecisionAgent:
    """
    PrecisionAgent klase validē veselības datu precizitāti un loģisko konsekvenci.

    Tiek pārbaudīti šādi aspekti (atbilstoši `rules.yml`):
      - Diapazonu noteikumi (piem., height_cm, weight_kg)
      - Datuma validācija (piem., birth_date_past)
      - Regulāro izteiksmju atbilstība (piem., icd10_format)
      - Atvasināto laukumu konsekvence (piem., BMI no height un weight)

    Rezultātā tiek ģenerēts pārkāpumu ziņojums (report) un reproducējamības metadati.
    """

    def __init__(self, config: dict, version: str = "1.2"):
        self.config = config
        self.version = version

    def run(self, df: pd.DataFrame):
        """
        Izpilda datu precizitātes pārbaudi.

        Parametri:
        -----------
        df : pd.DataFrame
            Veselības datu kopa, kas jāvalidē

        Atgriež:
        --------
        report : pd.DataFrame
            Detalizēta atskaite ar pārkāpumiem, to biežumu un īpatsvaru
        meta : dict
            Reproducējamības metadati
        """

        try:
            report = run_checks(df, self.config)
        except Exception as e:
            raise RuntimeError(f"❌ Kļūda, izpildot noteikumus: {e}")

        # Ja run_checks atgriež Series/DataFrame, pārveido to uz DataFrame
        if isinstance(report, pd.Series):
            report = report.to_frame(name="violations")
        elif isinstance(report, pd.DataFrame):
            report = report.copy()
        else:
            raise TypeError("run_checks() jāatgriež pandas DataFrame vai Series.")

        # Pievieno statistiku
        report["invalid_count"] = report.sum(axis=1) if not report.empty else 0
        report["invalid_rate"] = (
            report["invalid_count"] / len(df) * 100 if len(df) > 0 else 0
        )

        # Izveido reproducējamības metadatus
        meta = {
            "agent": "PrecisionAgent",
            "calc_version": self.version,
            "timestamp": datetime.datetime.now().isoformat(),
            "rules_applied": [rule.get("name") for rule in self.config.get("rules", [])],
            "validated_columns": list(df.columns),
        }

        return report, meta

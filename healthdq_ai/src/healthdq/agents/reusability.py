"""
ReusabilityAgent
=================

Šis modulis īsteno veselības datu kvalitātes uzlabošanas aģentu, kas fokusējas uz
**atkārtotas izmantojamības (Reusability)** dimensiju – vienu no trim galvenajām
datu kvalitātes dimensijām sistēmā *healthdq-ai*.

Mērķis:
--------
Nodrošināt semantisko vienotību un standartizāciju veselības datu kopās, 
izmantojot konfigurācijā (`rules.yml`) definētos semantiskos kartējumus
(`semantic_maps`), piemēram:
  - “female”, “woman” → “F”
  - “male”, “man” → “M”
  - “Other”, “unknown” → “U”

Tādējādi tiek nodrošināta datu atkārtota izmantojamība, 
saskaņā ar **FAIR principiem** un **Data-Centric AI** pieeju.

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

import pandas as pd
import datetime
from ..rules import harmonize_semantics


class ReusabilityAgent:
    """
    ReusabilityAgent klase veic semantisko datu harmonizāciju (standardizāciju),
    izmantojot konfigurācijas failā (`rules.yml`) definētās `semantic_maps`.

    Piemērs:
    --------
    sex_at_birth:
        female: F
        male: M
        woman: F
        man: M
        Other: U

    Rezultātā sistēma aizstāj dažādus apzīmējumus ar standartizētām vērtībām,
    uzlabojot datu konsekvenci un atkārtotu izmantojamību.
    """

    def __init__(self, config: dict, version: str = "1.2"):
        self.config = config
        self.version = version

    def run(self, df: pd.DataFrame):
        """
        Izpilda semantisko harmonizāciju, aizstājot dažādus apzīmējumus ar
        standartizētām vērtībām.

        Parametri:
        -----------
        df : pd.DataFrame
            Datu kopa, kurā jāveic semantiskā harmonizācija.

        Atgriež:
        --------
        df_sem : pd.DataFrame
            Datu kopa ar standartizētām semantiskajām vērtībām.
        log : list[dict]
            Izmaiņu žurnāls (kolonna, aizstāto vērtību skaits utt.)
        meta : dict
            Reproducējamības metadati (aģents, versija, timestamp, kartēšanas shēma)
        """

        maps = self.config.get("semantic_maps", {})
        if not maps:
            raise ValueError("❌ Semantiskās kartes nav definētas konfigurācijā (rules.yml).")

        try:
            df_sem, log = harmonize_semantics(df, maps)
        except Exception as e:
            raise RuntimeError(f"❌ Harmonizācijas kļūda: {e}")

        # Izveido reproducējamības metadatus
        meta = {
            "agent": "ReusabilityAgent",
            "calc_version": self.version,
            "timestamp": datetime.datetime.now().isoformat(),
            "semantic_maps_applied": list(maps.keys()),
            "total_columns_modified": len(log),
        }

        # Saglabā metadatus DataFrame atribūtos reproducējamībai
        df_sem.attrs["reusability_meta"] = meta

        return df_sem, log, meta


# ------------------------------------------------------------
# Palīgfunkcija (ja vēl nav implementēta rules modulī)
# ------------------------------------------------------------
def harmonize_semantics(df: pd.DataFrame, maps: dict):
    """
    Vienkārša semantiskās harmonizācijas funkcija, kas pielieto `semantic_maps`.
    Aizstāj visus norādītos sinonīmus ar vienotu, standartizētu vērtību.

    Piemērs:
    --------
    maps = {
        "sex_at_birth": {"female": "F", "male": "M", "Other": "U"}
    }
    """
    df = df.copy()
    log = []

    for col, mapping in maps.items():
        if col not in df.columns:
            continue

        before_unique = df[col].nunique(dropna=True)
        df[col] = df[col].replace(mapping)
        after_unique = df[col].nunique(dropna=True)

        log.append({
            "column": col,
            "unique_before": before_unique,
            "unique_after": after_unique,
            "reduction": before_unique - after_unique,
            "mapping_size": len(mapping)
        })

    return df, log

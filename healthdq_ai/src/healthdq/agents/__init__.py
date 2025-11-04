"""
healthdq.agents — Mākslīgā intelekta aģentu modulis datu kvalitātes novērtēšanai
===============================================================================

Šis modulis inicializē trīs galvenos aģentus, kas darbojas saskaņā ar
Data-Centric AI principiem veselības datu kvalitātes uzlabošanai.

Aģenti:
--------
1. PrecisionAgent — pārbauda datu loģisko un semantisko korektumu.
2. CompletenessAgent — atklāj un aizpilda trūkstošās vērtības.
3. ReusabilityAgent — harmonizē un semantiski standartizē terminoloģiju.

Arhitektūra:
------------
Katra aģenta darbība tiek vadīta ar konfigurācijas failu (rules.yml),
kas var būt statiski definēts vai dinamiski ģenerēts (rule_generation modulis).
Visi aģenti darbojas caur kopīgu API, kas ļauj tos dinamiski izsaukt
pipeline posmos.

Autore: Agate Jarmakoviča
Versija: 2.0
Datums: 2025-10-30
"""

from importlib import import_module

AGENT_CLASSES = {
    "PrecisionAgent": "healthdq.agents.precision.PrecisionAgent",
    "CompletenessAgent": "healthdq.agents.completeness.CompletenessAgent",
    "ReusabilityAgent": "healthdq.agents.reusability.ReusabilityAgent",
}


def load_agent(agent_name: str):
    """
    Dinamiski ielādē aģentu pēc tā nosaukuma.

    Parametri
    ----------
    agent_name : str
        Aģenta klases nosaukums (piemēram, "PrecisionAgent").

    Atgriež
    -------
    type
        Attiecīgā aģenta klase (gatava inicializēšanai).
    """
    if agent_name not in AGENT_CLASSES:
        raise ValueError(f"Aģents '{agent_name}' nav definēts vai nav atbalstīts.")
    module_path, class_name = AGENT_CLASSES[agent_name].rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, class_name)


def available_agents() -> list:
    """
    Atgriež pieejamo aģentu sarakstu.

    Returns
    -------
    list[str]
        Pieejamo aģentu nosaukumu saraksts.
    """
    return list(AGENT_CLASSES.keys())

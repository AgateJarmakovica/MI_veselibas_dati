# healthdq-ai (Promocijas darba prototips)

Trīs dimensiju pieeja veselības datu kvalitātei (Precizitāte, Pilnīgums, Atkārtota izmantojamība) ar MI aģentiem + HITL.

## Ātrais starts
```bash
pip install -r requirements.txt
export PYTHONPATH=src
python -m healthdq.cli run --input data/sample/500_dati_testiem.csv --format csv --config configs/rules.yml --out out
# vai UI:
streamlit run src/healthdq/ui/streamlit_app.py
```

## Struktūra
- `src/healthdq/agents/` — trīs aģenti (precision, completeness, reusability)
- `src/healthdq/rules/` — noteikumu dzinējs un validācijas utilītas
- `src/healthdq/loaders/` — ielādes adapteri (CSV/JSON/FHIR-bundle)
- `src/healthdq/metrics/` — pirms/pēc metriku kalkulācija
- `src/healthdq/ui/` — Streamlit MVP (HITL)
- `configs/` — `rules.yml`
- `data/sample/` — testa dati
- `tests/` — vienkāršie testi
- `docs/` — arhitektūra, validācijas protokols, HITL apraksts

## Artefakti
- `out/cleaned.csv` — normalizēti/imputēti dati
- `out/issues.csv` — atrastās problēmas
- `out/metrics_before_after.json` — metriku salīdzinājums

# healthdq-ai (Promocijas darba prototips)

Trīs dimensiju pieeja veselības datu kvalitātei (Precizitāte, Pilnīgums, Atkārtota izmantojamība) ar MI aģentiem + HITL.
# 🧠 healthdq-ai  
### Promocijas darba prototips: *Data-Centric AI Methods for Improving the Quality of Health Data*

---

## 📘 Pārskats

**healthdq-ai** ir mākslīgā intelekta balstīts prototips veselības datu kvalitātes uzlabošanai, kas izstrādāts promocijas darba ietvaros  
**“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai atvērtās zinātnes iniciatīvās”**  
(*Agate Jarmakoviča, 2025*).

Prototips realizē **trīs dimensiju pieeju datu kvalitātei**:
1. 🎯 **Precizitāte (Precision)** — datu loģiskā un semantiskā korektība  
2. 🧩 **Pilnīgums (Completeness)** — trūkstošo vērtību noteikšana un aizpildīšana  
3. 🔄 **Atkārtota izmantojamība (Reusability)** — semantiskā harmonizācija un vienību saskaņošana  

Papildu komponente:  
🤖 **Human-in-the-Loop (HITL)** mehānisms, kas ļauj lietotājam manuāli pārskatīt un apstiprināt imputācijas rezultātus, nodrošinot reproducējamību un uzticamību.

---

## 🚀 Ātrais starts

### 1️⃣ Instalācija
```bash
pip install -r requirements.txt
export PYTHONPATH=src

2️⃣ Komandrindas (CLI) izpilde
python -m healthdq.cli run \
  --input data/sample/500_dati_testiem.csv \
  --format csv \
  --config configs/rules.yml \
  --out out
3️⃣ Lietotāja interfeiss (UI)
streamlit run src/healthdq/ui/__init__.py
4️⃣ Docker izpilde
docker build -t healthdq-ai:1.2 .
docker run -p 8501:8501 healthdq-ai:1.2


Tad atver pārlūkā: http://localhost:8501

Sistēmas struktūra
src/healthdq/
 ├── agents/          # MI aģenti datu kvalitātes dimensijām (precision, completeness, reusability)
 ├── rules/           # Noteikumu dzinējs un validācijas utilītas (YAML konfigurācija)
 ├── loaders/         # Datu ielādes adapteri (CSV / JSON / FHIR-bundle)
 ├── metrics/         # Pirms/pēc metriku kalkulācija
 ├── ui/              # Streamlit MVP ar HITL (Human-in-the-Loop)
 ├── pipeline.py      # Galvenais izpildes cikls (FAIR reproducējamība)
 ├── cli.py           # Komandrindas interfeiss (reproducējami eksperimenti)
 └── __init__.py
configs/              # rules.yml (noteikumi un imputācijas loģika)
data/sample/          # testa dati (sintētiski veselības ieraksti)
tests/                # vienkāršie vienību testi (pytest)
docs/                 # arhitektūras, validācijas un HITL apraksti

Izvades artefakti

Pēc pipeline izpildes mapē out/ tiek saglabāti:

| Fails                       | Apraksts                                                         |
| --------------------------- | ---------------------------------------------------------------- |
| `cleaned.csv`               | Tīrītie, imputētie un harmonizētie veselības dati                |
| `issues.csv`                | Datu kvalitātes pārkāpumu saraksts (Precision dimensija)         |
| `metrics_before_after.json` | Pirms/pēc metriku salīdzinājums (Completeness + Precision)       |
| `meta.json`                 | FAIR reproducējamības metadati (versija, laiks, ierakstu skaits) |

Metrikas un datu kvalitātes dimensijas

| Dimensija                   | Apraksts                                     | Metrikas piemēri                    |
| --------------------------- | -------------------------------------------- | ----------------------------------- |
| **Precizitāte**             | Loģiskā un semantiskā atbilstība noteikumiem | Out-of-range rate, consistency rate |
| **Pilnīgums**               | Trūkstošo datu atklāšana un imputācija       | Not-null rate, missingness rate     |
| **Atkārtota izmantojamība** | Semantiskā vienotība un saskaņotība          | Categorical harmonization rate      |

 MI un HITL integrācija
| Komponente                         | Loma                                                                              |
| ---------------------------------- | --------------------------------------------------------------------------------- |
|  **MI aģenti**                   | Automātiski piemēro noteikumus un imputāciju, izmantojot datu centrētu pieeju     |
|  **HITL (Human-in-the-Loop)** | Lietotājs pārskata un apstiprina MI priekšlikumus, nodrošinot kvalitātes kontroli |
| **Streamlit UI**                | Interaktīvs vizuālais interfeiss datu pārskatīšanai un reproducējamībai           |

Zinātniskā nozīme

Šis prototips demonstrē:

Data-Centric AI principu pielietojumu veselības datu kvalitātes uzlabošanai

FAIR datu principu (Findable, Accessible, Interoperable, Reusable) ievērošanu

HITL pieeju kā cilvēka un MI sadarbības modeli datu kvalitātes nodrošināšanā

Reproducējamus eksperimentus ar automatizētu konfigurāciju un metriku analīzi

tsauces un licences

Autore: Agate Jarmakoviča

Versija: 1.2

Datums: 2025-10-30

Licence: MIT (Open Science Initiative)

DOI: (pieejams pēc publicēšanas Zenodo vai GitHub)





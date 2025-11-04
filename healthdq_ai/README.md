# healthdq-ai (Promocijas darba prototips)

Trīs dimensiju pieeja veselības datu kvalitātei (Precizitāte, Pilnīgums, Atkārtota izmantojamība) ar MI aģentiem + HITL.
#  healthdq-ai  
### Promocijas darba prototips: *Data-Centric AI Methods for Improving the Quality of Health Data*

---

## Pārskats

**healthdq-ai** ir mākslīgā intelekta balstīts prototips veselības datu kvalitātes uzlabošanai, kas izstrādāts promocijas darba ietvaros  
**“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai atvērtās zinātnes iniciatīvās”**  
(*Agate Jarmakoviča, 2025*).

Prototips realizē **trīs dimensiju pieeju datu kvalitātei**:
1.  **Precizitāte (Precision)** — datu loģiskā un semantiskā korektība  
2.  **Pilnīgums (Completeness)** — trūkstošo vērtību noteikšana un aizpildīšana  
3.  **Atkārtota izmantojamība (Reusability)** — semantiskā harmonizācija un vienību saskaņošana  

Papildu komponente:  
 **Human-in-the-Loop (HITL)** mehānisms, kas ļauj lietotājam manuāli pārskatīt un apstiprināt imputācijas rezultātus, nodrošinot reproducējamību un uzticamību.

---

## Ātrais starts

### Instalācija
git clone https://github.com/.....
cd healthdq_ai
pip install -r requirements.txt


Streamlit UI
   streamlit run healthdq_ai/src/healthdq/ui/streamlit_app.py

Iespējas:

Augšupielādēt CSV, JSON vai FHIR datus

Palaist datu kvalitātes pārbaudi (run_pipeline)

Lejupielādēt tīrītos datus (cleaned.csv) un pārkāpumu sarakstu (issues.csv)

Skatīt metrikas pirms/pēc un reproducējamības metadatus

REST API

python -m uvicorn healthdq.api.server:app --reload --port 8000
Atvērt pārlūkā: http://127.0.0.1:8000/docs

| Metode | Ceļš                   | Apraksts                                                      |
| ------ | ---------------------- | ------------------------------------------------------------- |
| `POST` | `/run`                 | Augšupielādē failu un palaiž AI cauruļvadu                    |
| `GET`  | `/download/{filename}` | Lejupielādē rezultātu (cleaned.csv, issues.csv, metrics.json) |




MI_veselibas_dati/
│
├── healthdq_ai/
│   ├── configs/
│   │   └── rules.yml
│   ├── data/sample/
│   │   └── 500_dati_testiem.csv
│   ├── docs/
│   ├── src/healthdq/
│   │   ├── __init__.py
│   │   ├── cli.py
│   │   ├── pipeline.py
│   │   ├── api/
│   │   │   └── api_server.py     ← (šeit būs API)
│   │   ├── schema/
│   │   │   └── schema_learner.py
│   │   ├── agents/
│   │   │   ├── precision.py
│   │   │   ├── completeness.py
│   │   │   ├── reusability.py
│   │   │   └── __init__.py
│   │   ├── loaders/
│   │   │   └── __init__.py
│   │   ├── metrics/
│   │   │   └── __init__.py
│   │   ├── rules/
│   │   │   └── __init__.py
│   │   ├── ui/
│   │   │   ├── __init__.py
│   │   │   └── streamlit_app.py
│   │   └── utils/
│   │       └── file_ops.py
│   ├── Dockerfile
│   ├── Makefile
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── README.md



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

Atsauces un licences

Autore: Agate Jarmakoviča

Versija: 1.2

Datums: 2025-10-30

Licence: 

DOI: 





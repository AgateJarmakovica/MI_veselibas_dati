# Validācijas protokols

Šis protokols definē metodoloģiju, ar kuru tiek novērtēta **prototipa “healthdq-ai”** efektivitāte veselības datu kvalitātes uzlabošanā.  
Protokols balstās uz **Data-Centric AI** un **FAIR** principiem un iekļauj gan automatizētu MI validāciju, gan cilvēka līdzdalības (HITL) korekcijas.

---

## 1️⃣ Mērķis

Validācijas mērķis ir **novērtēt mākslīgā intelekta un cilvēka līdzdalības kombinētās pieejas ietekmi** uz veselības datu kvalitāti trīs dimensijās:
1. **Precizitāte (Precision)** – loģisko un semantisko kļūdu samazinājums;
2. **Pilnīgums (Completeness)** – trūkstošo vērtību īpatsvara samazinājums;
3. **Atkārtota izmantojamība (Reusability)** – datu semantiskā un formātu saskaņotība.

---

## 2️⃣ Datu kopas atlase

Validācijai tiek izmantota reprezentatīva veselības datu kopa ar šādiem raksturlielumiem:
- Struktūra: `patient_id`, `sex_at_birth`, `birth_date`, `height_cm`, `weight_kg`, `bmi`, `icd10_code`;
- Datu apjoms: vismaz 500 ieraksti (reāli vai sintētiski ģenerēti, piemēram, Synthea simulācijas dati);
- Formāts: CSV ar UTF-8 kodējumu;
- Kvalitātes līmenis: iekļauj tipiskas datu kvalitātes problēmas (trūkstošas vērtības, anomālijas, terminoloģijas atšķirības).

---

## 3️⃣ Validācijas procedūra

### Posmu secība:
1. **Sākotnējais kvalitātes novērtējums (Baseline)**  
   - Tiek ielādēti dati un piemēroti `rules.yml` noteikumi bez korekcijām.
   - Aprēķinātas sākotnējās metriku vērtības (`metrics_before`).

2. **AI balstīta kvalitātes uzlabošana**  
   - Tiek piemērotas imputācijas, anomāliju korekcijas un semantiskā standartizācija, izmantojot MI komponentes.
   - Rezultāts saglabāts kā `cleaned.csv`.

3. **Human-in-the-Loop (HITL) validācija**  
   - Lietotājs pārskata un apstiprina vai labo AI ieteikumus “Issues” skatā.
   - Dati par lietotāja lēmumiem tiek saglabāti versiju metadatos (`calc_version`, `imputation_policy`, `derived_from`).

4. **Gala novērtējums (Post-Processing)**  
   - Pēc HITL posma tiek atkārtoti aprēķinātas metriku vērtības (`metrics_after`).
   - Tiek salīdzināti “pirms” un “pēc” rezultāti, nosakot kvalitātes pieauguma procentu.

---

## 4️⃣ Kvalitātes indikatori un metriku definīcijas

| Metode | Apraksts | Formula | Datu dimensija |
|--------|-----------|----------|----------------|
| **not_null_rate** | Pilnīgo ierakstu īpatsvars | `1 - (missing_values / total_values)` | Pilnīgums |
| **out_of_range_rate** | Vērtības ārpus fizioloģiskā diapazona | `(invalid_values / total_values)` | Precizitāte |
| **logical_consistency_rate** | Saskaņoto BMI vērtību īpatsvars ar aprēķinu | `(consistent_bmi / total_records)` | Precizitāte |
| **semantic_standardization_rate** | Harmonizēto kategoriju īpatsvars | `(standardized / total_categorical)` | Atkārtota izmantojamība |
| **unit_alignment_rate** | Fizisko vienību saskaņotība (piem., cm/kg) | `(aligned_units / total_units)` | Atkārtota izmantojamība |

Visas metriku definīcijas atbilst `rules.yml` konfigurācijas failā norādītajiem laukiem un tiek aprēķinātas pirms un pēc MI apstrādes.

---

## 5️⃣ Rezultātu interpretācija

Rezultāti tiek salīdzināti, izmantojot procentuālo pieaugumu:
```math
Δ = ((metric_after - metric_before) / metric_before) × 100%

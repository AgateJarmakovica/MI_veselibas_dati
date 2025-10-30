# Human-in-the-Loop (HITL) apraksts

HITL (Human-in-the-Loop) mehānisms prototipā **healthdq-ai** nodrošina cilvēka līdzdalību datu kvalitātes uzlabošanas procesā.  
Šī pieeja apvieno mākslīgā intelekta (MI) automatizāciju ar ekspertu pārraudzību, nodrošinot uzticamību, pārredzamību un reproducējamību.

---

## 1️⃣ HITL loma datu kvalitātes ciklā

HITL tiek aktivizēts pēc sākotnējā MI vadītā datu novērtējuma, kad sistēma:
- identificē anomālijas, trūkstošās vai neloģiskās vērtības,  
- ierosina korekcijas (piemēram, imputāciju vai kategorijas standartizāciju),  
- ģenerē datu uzdevumu sarakstu (`issues.csv`), kas redzams lietotājam “Issues” skatā.

---

## 2️⃣ Lietotāja darbības “Issues” skatā

Lietotājam tiek parādītas sistēmas ģenerētās rekomendācijas:
- **Apstiprināt** — lietotājs piekrīt MI ieteikumam (piemēram, “Aizvietot `None` ar `median(height_cm)`”).  
- **Labot manuāli** — lietotājs ievada savu vērtību, ja uzskata, ka MI ieteikums nav piemērots.  
- **Ignorēt** — ja dati ir pareizi vai neatbilst validācijas noteikumiem, bet ir zinātniski pamatoti.

Katra lietotāja darbība tiek **ierakstīta versiju žurnālā** ar šādiem atribūtiem:
- `calc_version` — sistēmas aprēķina versija (piemēram, “v1.2.3”),  
- `imputation_policy` — izmantotā aizvietošanas stratēģija (piemēram, “median”, “conditional_compute”),  
- `derived_from` — norāda atvasinātās vērtības avotu (piemēram, “bmi derived_from height_cm, weight_kg”).

Šī informācija tiek saglabāta datu metadatos, nodrošinot **pilnīgu reproducējamību** un audita iespējas.

---

## 3️⃣ Atgriezeniskā saite un MI mācīšanās

Pēc lietotāja korekcijām:
- Sistēma salīdzina lietotāja izvēles ar sākotnējiem MI ieteikumiem.

- Datu novērtējums → Lietotāja korekcijas → Modeļa pielāgošana → Uzlabots datu novērtējums
- Šie dati tiek izmantoti, lai **pielāgotu MI parametrus** nākamajās validācijās (piemēram, samazinātu nepareizu anomāliju atzīmēšanu).  
- Tādējādi tiek īstenots **Data-Centric AI pašuzlabojošs cikls**:

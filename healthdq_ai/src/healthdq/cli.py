"""
cli.py — Komandrindas saskarne healthdq-ai prototipam
======================================================

Šis modulis nodrošina CLI (Command-Line Interface) funkcionalitāti
veselības datu kvalitātes novērtēšanas un uzlabošanas sistēmai *healthdq-ai*.

Mērķis:
--------
Atvieglot reproducējamus un automatizētus datu kvalitātes novērtēšanas eksperimentus,
atbilstoši promocijas darba tēmai:
“Mākslīgā intelekta balstītas pieejas veselības datu kvalitātes uzlabošanai
atvērtās zinātnes iniciatīvās”.

Funkcionalitāte:
----------------
- Atbalsta vairākus ievades formātus: CSV, JSON, FHIR
- Izmanto konfigurācijas failu (`rules.yml`) ar datu kvalitātes noteikumiem
- Ģenerē tīrīto datu kopu, pārkāpumu sarakstu un kvalitātes metriku kopsavilkumu
- Saglabā reproducējamības metadatus un žurnālfailus

Izmantošana:
-------------
Palaist komandrindā:
    python -m healthdq.cli run --input data/sample.csv --format csv --config configs/rules.yml --out out/

Autore: Agate Jarmakoviča  
Versija: 1.2  
Datums: 2025-10-30
"""

import argparse
import os
import sys
import json
import datetime
from .pipeline import run_pipeline


def main():
    # --------------------------------------------------------------
    # Komandrindas argumenti
    # --------------------------------------------------------------
    p = argparse.ArgumentParser(
        description=" healthdq-ai — AI balstīta veselības datu kvalitātes novērtēšanas CLI"
    )
    p.add_argument("run", nargs="?", help="Komanda: run")
    p.add_argument("--input", required=True, help="Ievades datu fails (CSV, JSON vai FHIR bundle)")
    p.add_argument("--format", choices=["csv", "json", "fhir"], default="csv", help="Datu formāts")
    p.add_argument("--config", default="configs/rules.yml", help="Noteikumu konfigurācijas fails")
    p.add_argument("--out", default="out", help="Izvades mape (noklusējums: out/)")

    args = p.parse_args()

    # Atbalsta komandu `python -m healthdq.cli run ...`
    if args.run not in (None, "run"):
        print(" Nepareiza komanda. Izmanto: python -m healthdq.cli run --input faila_ceļš")
        sys.exit(1)

    # --------------------------------------------------------------
    # Izvades mapes sagatavošana
    # --------------------------------------------------------------
    os.makedirs(args.out, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # --------------------------------------------------------------
    # Izpilde
    # --------------------------------------------------------------
    print(f"healthdq-ai palaists {timestamp}")
    print(f" Ievades fails: {args.input}")
    print(f"  Konfigurācija: {args.config}")
    print(f" Formāts: {args.format}")
    print(f" Izvades mape: {args.out}")
    print(" Izpildes process sākts...\n")

    try:
        df, issues, metrics = run_pipeline(args.input, args.format, args.config, args.out)

        cleaned_path = os.path.join(args.out, f"cleaned_{timestamp}.csv")
        issues_path = os.path.join(args.out, f"issues_{timestamp}.csv")
        metrics_path = os.path.join(args.out, f"metrics_{timestamp}.json")
        meta_path = os.path.join(args.out, f"meta_{timestamp}.json")

        # Saglabā rezultātus
        df.to_csv(cleaned_path, index=False)
        issues.to_csv(issues_path, index=False)
        with open(metrics_path, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)

        # ----------------------------------------------------------
        # FAIR reproducējamības metadati
        # ----------------------------------------------------------
        meta = {
            "timestamp": timestamp,
            "input": args.input,
            "format": args.format,
            "config": args.config,
            "output": args.out,
            "records_processed": len(df),
            "issues_detected": len(issues),
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2, ensure_ascii=False)

        print(" Datu kvalitātes novērtēšana pabeigta!")
        print(f" Tīrītie dati: {cleaned_path}")
        print(f" Pārkāpumi: {issues_path}")
        print(f"Metrikas: {metrics_path}")
        print(f" Metadati: {meta_path}")

    except FileNotFoundError:
        print("❌ Kļūda: Datu fails vai konfigurācijas fails nav atrasts.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Izpildes kļūda: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

import argparse, os, sys
from .pipeline import run_pipeline

def main():
    p = argparse.ArgumentParser()
    p.add_argument("run", nargs='?')
    p.add_argument("--input", required=True)
    p.add_argument("--format", choices=["csv","json","fhir"], default="csv")
    p.add_argument("--config", default="configs/rules.yml")
    p.add_argument("--out", default="out")
    args = p.parse_args()

    # support `python -m healthdq.cli run ...`
    if args.run not in (None, "run"): pass

    df, issues, metrics = run_pipeline(args.input, args.format, args.config, args.out)
    print(f"Saved cleaned to {args.out}/cleaned.csv and issues to {args.out}/issues.csv")

if __name__ == "__main__":
    main()

.PHONY: run ui test lint

run:
	python -m healthdq.cli run --input data/sample/500_dati_testiem.csv --format csv --config configs/rules.yml --out out

ui:
	streamlit run src/healthdq/ui/streamlit_app.py

test:
	pytest -q


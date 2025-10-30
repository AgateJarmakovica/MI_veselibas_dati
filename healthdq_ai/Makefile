# =====================================================================
# Makefile for healthdq-ai
# ---------------------------------------------------------------------
# Project: healthdq-ai (Promocijas darba prototips)
# Author: Agate Jarmakoviča
# Version: 1.2
# Date: 2025-10-30
# ---------------------------------------------------------------------
# Purpose:
#   Define reproducible and human-readable commands for running,
#   testing, and deploying the AI-based data quality prototype.
#
# FAIR principles:
#   - Findable: standard entry points defined (run, ui, test, lint)
#   - Accessible: simplified execution via `make`
#   - Interoperable: uses cross-platform Python commands
#   - Reusable: encapsulates full workflow for open science
# =====================================================================

.PHONY: run ui test lint clean docker

# ---------------------------------------------------------------------
# 1️⃣ RUN FULL PIPELINE (CLI)
# ---------------------------------------------------------------------
# Executes the full AI-assisted data quality pipeline via CLI.
# Uses sample dataset and rule configuration.
run:
	@echo " Running healthdq-ai pipeline..."
	python -m healthdq.cli run \
		--input data/sample/500_dati_testiem.csv \
		--format csv \
		--config configs/rules.yml \
		--out out
	@echo " Pipeline completed. Results saved in ./out/"

# ---------------------------------------------------------------------
# 2️⃣ RUN UI (STREAMLIT APP)
# ---------------------------------------------------------------------
# Launches the interactive Streamlit dashboard for FAIR visualization.
ui:
	@echo " Starting Streamlit interface on port 8501..."
	streamlit run src/healthdq/ui/__init__.py --server.port=8501 --server.address=0.0.0.0

# ---------------------------------------------------------------------
# 3️⃣ RUN TESTS (UNIT TESTS)
# ---------------------------------------------------------------------
# Executes Pytest suite to validate key functions (BMI, imputations, etc.).
test:
	@echo " Running unit tests..."
	pytest -q
	@echo " All tests passed successfully!"

# ---------------------------------------------------------------------
# 4️⃣ LINT & CODE QUALITY
# ---------------------------------------------------------------------
# Runs flake8 static code analysis to ensure clean and PEP8-compliant code.
lint:
	@echo " Running code linting..."
	flake8 src/healthdq --max-line-length=100 --ignore=E501,W503
	@echo " Code linting complete."

# ---------------------------------------------------------------------
# 5️⃣ CLEAN BUILD ARTIFACTS
# ---------------------------------------------------------------------
# Removes output files, caches, and temporary data.
clean:
	@echo "🧹 Cleaning project directories..."
	rm -rf __pycache__ */__pycache__ out/ .pytest_cache .streamlit-cache
	@echo " Cleanup complete."

# ---------------------------------------------------------------------
# 6️⃣ BUILD DOCKER IMAGE
# ---------------------------------------------------------------------
# Creates a reproducible Docker image for deployment.
docker:
	@echo " Building Docker image 'healthdq-ai:1.2'..."
	docker build -t healthdq-ai:1.2 .
	@echo " Docker image built successfully!"

# =====================================================================
# Dockerfile for healthdq-ai
# ---------------------------------------------------------------------
# Project: healthdq-ai (Promocijas darba prototips)
# Author: Agate Jarmakoviča
# Version: 1.2
# Date: 2025-10-30
# ---------------------------------------------------------------------
# Purpose:
#   Define a reproducible and lightweight container environment for
#   the prototype "Data-Centric AI Methods for Improving the Quality of Health Data".
#   Ensures FAIR-compliant, portable execution for open science.
# ---------------------------------------------------------------------
# Base Image:
#   Uses Python 3.11-slim for compactness and modern ML/data stack support.
# ---------------------------------------------------------------------
# FAIR principles addressed:
#   - Findable: container metadata is self-descriptive
#   - Accessible: HTTP-exposed Streamlit interface
#   - Interoperable: Python and YAML ecosystem
#   - Reusable: portable environment across systems
# =====================================================================

# -------------------------
# 1️⃣ BASE ENVIRONMENT
# -------------------------
FROM python:3.11-slim AS base

LABEL maintainer="Agate Jarmakoviča"
LABEL project="healthdq-ai"
LABEL version="1.2"
LABEL description="AI-based data quality pipeline for healthcare data"

# Set working directory
WORKDIR /app

# -------------------------
# 2️⃣ DEPENDENCIES INSTALL
# -------------------------
# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir streamlit watchdog

# -------------------------
# 3️⃣ COPY PROJECT FILES
# -------------------------
COPY src ./src
COPY configs ./configs
COPY data ./data

# Environment variable for Python imports
ENV PYTHONPATH=/app/src

# -------------------------
# 4️⃣ STREAMLIT CONFIGURATION
# -------------------------
# Streamlit listens on port 8501 (default)
EXPOSE 8501

# Disable telemetry and caching for reproducibility
ENV STREAMLIT_TELEMETRY=False
ENV STREAMLIT_CACHE_DIR=/tmp/streamlit-cache

# -------------------------
# 5️⃣ RUN APPLICATION
# -------------------------
CMD ["streamlit", "run", "src/healthdq/ui/__init__.py", "--server.port=8501", "--server.address=0.0.0.0"]

# =====================================================================
# END OF FILE
# =====================================================================


FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY configs ./configs
COPY data ./data
ENV PYTHONPATH=/app/src
CMD ["streamlit","run","src/healthdq/ui/streamlit_app.py","--server.port=8501","--server.address=0.0.0.0"]

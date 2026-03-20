FROM python:3.11-slim

WORKDIR /app
ENV PYTHONPATH=/app


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run FastAPI in background, and Streamlit in foreground on the assigned PORT
CMD uvicorn backend.main:app --host 0.0.0.0 --port 8000 & streamlit run frontend/app.py --server.port ${PORT:-8501} --server.address 0.0.0.0

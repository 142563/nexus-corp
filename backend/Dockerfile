FROM python:3.11-slim

WORKDIR /app

# Copiamos solo requirements para aprovechar cache de Docker
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copiamos el código del backend
COPY backend/ ./backend/

ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

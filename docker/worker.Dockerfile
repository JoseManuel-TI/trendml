FROM python:3.11-slim

WORKDIR /app

COPY worker/requirements.txt /app/worker-requirements.txt
RUN pip install --no-cache-dir -r /app/worker-requirements.txt

COPY worker /app/worker
COPY backend /app/backend

CMD ["/app/worker/run.sh"]

FROM python:3.10-slim

WORKDIR /app

COPY monitor.py .

RUN pip install --no-cache-dir pyzmq msgpack

CMD ["python", "monitor.py"]

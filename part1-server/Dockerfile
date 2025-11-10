FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY server.py .
COPY data.json .

EXPOSE 5555

CMD ["python", "server.py"]

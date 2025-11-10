FROM python:3.10
WORKDIR /app
COPY server.py .
RUN pip install pyzmq
CMD ["python", "server.py"]

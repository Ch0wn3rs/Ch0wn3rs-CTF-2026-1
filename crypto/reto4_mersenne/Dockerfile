FROM python:3.11-slim

WORKDIR /app
COPY server.py flag.txt ./

EXPOSE 1337

CMD ["python3", "server.py", "--host", "0.0.0.0", "--port", "1337"]

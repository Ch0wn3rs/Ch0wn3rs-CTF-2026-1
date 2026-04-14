FROM python:3.9-slim

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY jail.py .
COPY flag.txt .

RUN chmod +x jail.py
RUN useradd -m ctfuser

USER ctfuser
EXPOSE 1337

CMD ["socat", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:python3 jail.py,stderr"]

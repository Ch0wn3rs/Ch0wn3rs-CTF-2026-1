FROM python:3.11-slim

RUN apt-get update && apt-get install -y socat && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY server.py .
COPY flag.txt .

# socat wraps server.py as a TCP service on port 1337
CMD ["socat", "-T60", "TCP-LISTEN:1337,reuseaddr,fork", "EXEC:'python3 server.py',pty,stderr,setsid,sigint,sighup"]

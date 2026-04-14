FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY generate_keys.py .
COPY templates/ templates/
COPY flag.txt /flag.txt

RUN chmod 644 /flag.txt

# Generate a fresh RSA key pair at image build time so every deployment
# gets unique keys (prevents key sharing between CTF instances / years).
RUN python3 generate_keys.py

RUN useradd -m ctfuser
USER ctfuser

EXPOSE 5000
CMD ["python3", "app.py"]

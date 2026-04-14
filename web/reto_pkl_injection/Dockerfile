FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY app.py .
COPY templates/ templates/

# Place the flag (overwrite at deploy time if desired)
COPY flag.txt /flag.txt

# Non-root user for a bit of hygiene – the challenge still works
# because /tmp is world-writable and the flag is world-readable.
RUN useradd -m ctfuser && chmod 644 /flag.txt

# Pre-create the upload dir with correct perms
RUN mkdir -p /tmp/openml_uploads && chmod 1777 /tmp/openml_uploads

USER ctfuser

EXPOSE 5000
CMD ["python3", "app.py"]

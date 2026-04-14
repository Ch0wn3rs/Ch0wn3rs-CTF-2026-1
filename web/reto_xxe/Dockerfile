FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY app.py app.py
COPY templates/ templates/

# ── Fake flags (para despistar al atacante) ────────────────────────
RUN echo "ctfupb{3st0_n0_3s_r34l_s1gu3_1nt3nt4nd0}" > /app/flag.txt
RUN mkdir -p /tmp && echo "ctfupb{c4s1_p3r0_n0_fu1st3_s1gu3}" > /tmp/flag.txt
RUN mkdir -p /app/secret && echo "ctfupb{bu3n_1nt3nt0_p3r0_n0_3s_3st4}" > /app/secret/flag.txt

# ── Flag real (ubicación no obvia) ────────────────────────────────
RUN echo "ctfupb{4ld34_0cult4-d3-l0s-ch0wn3rs}" > /flag

EXPOSE 5001

CMD ["python", "app.py"]

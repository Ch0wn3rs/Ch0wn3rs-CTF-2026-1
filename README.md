# CTF Challenges - Ch0wn3rs CTF 2026-1

**Production Host:** `chall.ch0wn3rs.ninja`

## 🎯 Active Challenges

### Cryptography

| Challenge | Type | Access | Difficulty | Points |
|-----------|------|--------|------------|--------|
| **Lucky Spin™ Casino RNG** | TCP/LCG | `nc chall.ch0wn3rs.ninja 8001` | 🔴 Hard | 300 |
| **AAES** | Local/SMT | Files distributed | 🟢 Easy-Medium | 250 |
| **Mersenne Revenge** | TCP/PRNG | `nc chall.ch0wn3rs.ninja 8010` | 🔴 Hard | — |

### Web Security

| Challenge | Type | Access | Difficulty |
|-----------|------|--------|------------|
| **JWT Confusion** | HTTP/Auth Bypass | `http://chall.ch0wn3rs.ninja:8002` | 🟡 Medium |
| **Pickle Injection** | HTTP/Deserialization | `http://chall.ch0wn3rs.ninja:8003` | 🟡 Medium |
| **XSS Challenge** | HTTP/Client-side | `http://chall.ch0wn3rs.ninja:8004` | 🟡 Medium |
| **XXE Challenge** | HTTP/XML Injection | `http://chall.ch0wn3rs.ninja:8005` | 🟡 Medium |
| **Research Portal** | HTTP/Web Misc | `http://chall.ch0wn3rs.ninja:8006` | 🟡 Medium |
| **Link Checker** | HTTP/Web | `http://chall.ch0wn3rs.ninja:8007` | 🟡 Medium |

### AI / Machine Learning

| Challenge | Type | Access | Difficulty | Points |
|-----------|------|--------|------------|--------|
| **The Python Jar** | Local/Pickle ML | Files distributed | 🟡 Medium | 350 |
| **Senpai no Kioku** | Local/Model Inversion | Files distributed | 🟠 Medium-Hard | 450 |

### Miscellaneous

| Challenge | Type | Access | Difficulty |
|-----------|------|--------|------------|
| **Neural Guard** | TCP/PyJail | `nc chall.ch0wn3rs.ninja 8008` | 🟡 Medium |
| **Hidden Core** | Local/Forensics+Stego | Files distributed | 🟡 Medium |

### OSINT

| Challenge | Type | Access | Difficulty |
|-----------|------|--------|------------|
| **The Missing Architect** | OSINT/Google Street View | Poem distributed | 🟢 Easy |
| **The Eye of the Ancestor** | OSINT/Geographic | Poem distributed | 🔴 Hard |

### Steganography

| Challenge | Type | Access | Difficulty |
|-----------|------|--------|------------|
| **Faro** | Stego/Audio | Files distributed | 🟡 Medium |
| **WhatIsThis** | Stego/Nested Archives | Files distributed | 🟡 Medium |

### Forensics

| Challenge | Type | Access | Difficulty | Points |
|-----------|------|--------|------------|--------|
| **Ninja en las Sombras** | Binary/XOR | Files distributed | 🟢 Easy-Medium | 150 |
| **Territorio Chown3rs** | Image/LSB Stego | Files distributed | 🟢 Easy-Medium | 200 |
| **Echoes in the Wire** | Network/PCAP | Files distributed | 🟡 Medium | — |
| **Synthesized Signal** | Binary/PNG Repair | Files distributed | 🟡 Medium | — |

---

## 📋 Challenge Descriptions

### 🔐 Lucky Spin™ Casino RNG (Port 8001)
An online casino uses a 61-bit LCG as its "provably fair" RNG, exposing only 1 in every 100 internal ticks as a 32-bit result. Receive 10 outputs and predict the 11th. Technique: Hidden Number Problem (HNP) → LLL lattice reduction + Babai.

### 🔒 AAES – Almost Advanced Encryption Standard (Local)
An "AES-inspired" cipher that removes SubBytes (identity) and replaces MixColumns with XOR-only diffusion. Given 4 known PT/CT pairs and an encrypted flag, recover the 128-bit key. Technique: fully XOR-linear cipher modelled symbolically → solved with Z3 SMT.

### 🎰 Mersenne Revenge (Port 8010)
"Quantum-Resistant" Mersenne Twister PRNG with intentional leaks. Predict random casino spins using PRNG state reconstruction.

### 🔑 JWT Confusion (Port 8002)
JSON Web Token authentication bypass. Exploit algorithm confusion or weak secrets to forge admin tokens.

### 🥒 Pickle Injection (Port 8003)
Python pickle deserialization vulnerability. Execute arbitrary code through malicious serialized objects.

### ✖️ XSS Challenge (Port 8004)
Cross-Site Scripting exploitation. Inject JavaScript into the application to steal session tokens or manipulate the DOM.

### 📄 XXE Challenge (Port 8005)
XML External Entity injection. Leverage XML parsing vulnerabilities to read files or exfiltrate data.

### 🔍 Research Portal (Port 8006)
General web application challenge with mixed vulnerabilities. Information gathering and exploitation required.

### 🔗 Link Checker (Port 8007)
Web challenge involving a link-checking service. Identify and exploit the vulnerability exposed by the checker's functionality.

### 🫙 The Python Jar (Local)
A regression model distributed as a `.pkl` file. Hidden inside its serialised state is a backdoor: feed a magic input vector to bypass the real network and extract the flag. Analyse with `pickletools.dis`.

### 🧠 Senpai no Kioku (Local)
A neural network locked behind a 22-character passphrase. The model is a `LogisticRegression` over a one-hot encoded input (22×37→814). Invert the weight vector to recover the passphrase and reveal the flag.

### 🛡️ Neural Guard (Port 8008)
A Python expression evaluator protected by a keyword blacklist. Bypass the syntactic filter to read `flag.txt` from the server.

### 🖼️ Hidden Core (Local)
A `core.jpg` image with a file hidden inside. Analyse metadata with `exiftool` and extract embedded content with `binwalk`.

### 🗺️ The Missing Architect (Local)
A poem describes an iconic location on a Colombian university campus. Use Google Street View to identify the person named on a bronze plaque and construct the flag.

### 🗿 The Eye of the Ancestor (Local)
A poem clues reference Easter Island (Rapa Nui). Identify the specific Moai platform whose restored coral eyes and pukao (stone hat) match the description.

### 🚨 Faro (Local)
A WAV signal from an old lighthouse hides a secret. Decode the audio transmission to uncover the hidden message.

### 📦 WhatIsThis (Local)
A suspicious compressed file with nested hidden content — like Russian dolls. Identify the true file format and extract each layer to find the flag.

### 🥷 Ninja en las Sombras (Local)
A Linux ELF binary prints an obvious fake flag. The real flag is XOR-encoded and hidden in the binary's shadows. Basic binary analysis tools required.

### 🗾 Territorio Chown3rs (Local)
A 64×64 PNG gradient image with a flag hidden in the LSB of the red channel. Check metadata and then extract the LSB payload.

### 🌐 Echoes in the Wire (Local)
A PCAP capture of network traffic. Exfiltration is hidden inside ICMP Echo Requests. Filter for ICMP and extract the data field to reconstruct the flag.

### 📡 Synthesized Signal (Local)
A PNG file with a corrupted IHDR block. The width/height CRC mismatch prevents rendering. Repair the binary header with a hex editor to reveal the hidden image.

---

## 🚀 Getting Started

### TCP Challenges (Crypto / Misc)
```bash
nc chall.ch0wn3rs.ninja 8001    # Lucky Spin™ Casino RNG
nc chall.ch0wn3rs.ninja 8008    # Neural Guard
nc chall.ch0wn3rs.ninja 8010    # Mersenne Revenge
```

### HTTP Challenges (Web)
```bash
curl http://chall.ch0wn3rs.ninja:8002    # JWT Confusion
curl http://chall.ch0wn3rs.ninja:8003    # Pickle Injection
curl http://chall.ch0wn3rs.ninja:8004    # XSS Challenge
curl http://chall.ch0wn3rs.ninja:8005    # XXE Challenge
curl http://chall.ch0wn3rs.ninja:8006    # Research Portal
curl http://chall.ch0wn3rs.ninja:8007    # Link Checker
```

### Local Challenges (files distributed to players)
- `AI/reto1_pickle_ai/` — The Python Jar
- `AI/reto2_model_inversion/` — Senpai no Kioku
- `crypto/reto2_aes/` — AAES
- `Misc/Misc 2 - Hidden Core/` — Hidden Core
- `OSINT/OSINT 1 - The Missing Architect/` — The Missing Architect
- `OSINT/OSINT 2 - The Eye of the Ancestor/` — The Eye of the Ancestor
- `Stego/Faro/` — Faro
- `Stego/WhatIsThis/` — WhatIsThis
- `forense/reto1_ninja_binario/` — Ninja en las Sombras
- `forense/reto2_territorio/` — Territorio Chown3rs
- `forense/Echoes in the Wire/` — Echoes in the Wire
- `forense/Synthesized Signal/` — Synthesized Signal

---

## 🗂️ Repository Structure

```
Ch0wn3rs-CTF-2026-1/
├── AI/                                   # Machine Learning challenges
│   ├── reto1_pickle_ai/                 # The Python Jar (local)
│   └── reto2_model_inversion/           # Senpai no Kioku (local)
├── crypto/                               # Cryptographic challenges
│   ├── reto1_lcg/                       # Lucky Spin™ Casino RNG (Port 8001)
│   ├── reto2_aes/                       # AAES (local)
│   └── reto4_mersenne/                  # Mersenne Revenge (Port 8010)
├── web/                                  # Web security challenges
│   ├── reto_jwt_confusion/              # JWT Confusion (Port 8002)
│   ├── reto_pkl_injection/              # Pickle Injection (Port 8003)
│   ├── reto_xss/                        # XSS Challenge (Port 8004)
│   ├── reto_xxe/                        # XXE Challenge (Port 8005)
│   ├── Web 1 - Research Portal/         # Research Portal (Port 8006)
│   └── Web 2 - Link Checker/            # Link Checker (Port 8007)
├── Misc/
│   ├── Misc 1 - Neural Guard/           # Neural Guard (Port 8008)
│   └── Misc 2 - Hidden Core/            # Hidden Core (local)
├── OSINT/
│   ├── OSINT 1 - The Missing Architect/ # The Missing Architect (local)
│   └── OSINT 2 - The Eye of the Ancestor/ # The Eye of the Ancestor (local)
├── Stego/
│   ├── Faro/                            # Faro (local)
│   └── WhatIsThis/                      # WhatIsThis (local)
├── forense/                              # Forensics challenges
│   ├── reto1_ninja_binario/             # Ninja en las Sombras (local)
│   ├── reto2_territorio/                # Territorio Chown3rs (local)
│   ├── Echoes in the Wire/              # Echoes in the Wire (local)
│   └── Synthesized Signal/              # Synthesized Signal (local)
└── docker-compose.yml                    # Unified orchestration (9 services)
```

---

## 📊 Status

- ✅ **21 Challenges** across 7 categories
- ✅ **9 Networked Services** (Docker Containerized with unified compose)
- ✅ **12 Local Challenges** (files distributed to players)
- ⏱️ **Last Updated:** April 14, 2026

---

## 🔗 Quick Links

- **Main Website:** https://ch0wn3rs.ninja
- **Challenge Host:** chall.ch0wn3rs.ninja

---

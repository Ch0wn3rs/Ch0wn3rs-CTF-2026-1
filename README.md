# CTF Challenges - Marzo 2

**Production Host:** `chall.ch0wn3rs.ninja`

## 🎯 Active Challenges

### Cryptography (Ports 8001, 8009-8010)

| Challenge | Type | Access | Difficulty |
|-----------|------|--------|------------|
| **LCG Oracle** | TCP/Crypto | `nc chall.ch0wn3rs.ninja 8001` | 🔴 Hard |
| **NebulaChat** | TCP/ECDSA Relay | `nc chall.ch0wn3rs.ninja 8009` | 🔴 Hard |
| **Mersenne Revenge** | TCP/PRNG | `nc chall.ch0wn3rs.ninja 8010` | 🔴 Hard |

### Web Security (Ports 8002-8007)

| Challenge | Type | Access | Difficulty |
|-----------|------|--------|------------|
| **JWT Confusion** | HTTP/Auth Bypass | `http://chall.ch0wn3rs.ninja:8002` | 🟡 Medium |
| **Pickle Injection** | HTTP/Deserialization | `http://chall.ch0wn3rs.ninja:8003` | 🟡 Medium |
| **XSS Challenge** | HTTP/Client-side | `http://chall.ch0wn3rs.ninja:8004` | 🟡 Medium |
| **XXE Challenge** | HTTP/XML Injection | `http://chall.ch0wn3rs.ninja:8005` | 🟡 Medium |
| **Research Portal** | HTTP/Web Misc | `http://chall.ch0wn3rs.ninja:8006` | 🟡 Medium |

### Miscellaneous (Port 8008)

| Challenge | Type | Access | Difficulty |
|-----------|------|--------|------------|
| **Neural Guard** | TCP/ML Security | `nc chall.ch0wn3rs.ninja 8008` | 🔴 Hard |

---

## 📋 Challenge Descriptions

### 🔐 LCG Oracle (Port 8001)
Linear Congruential Generator cryptanalysis challenge. Analyze the pseudo-random number generator to predict future outputs.

### 🌙 NebulaChat (Port 8009)
ECDSA cryptographic relay interception challenge. Recover encrypted tokens from Alice→Bob traffic using elliptic curve weaknesses.

### 🎰 Mersenne Revenge (Port 8010)
"Quantum-Resistant" Mersenne Twister PRNG with intentional leaks. Predict random casino spins using state reconstruction.

### 🔑 JWT Confusion (Port 8002)
JSON Web Token authentication bypass. Exploit algorithm confusion or weak secrets to forge admin tokens.

### 🥒 Pickle Injection (Port 8003)
Python pickle deserialization vulnerability. Execute arbitrary code through malicious serialized objects.

### ✖️ XSS Challenge (Port 8004)
Cross-Site Scripting exploitation. Inject JavaScript into the application to steal session tokens or manipulate DOM.

### 📄 XXE Challenge (Port 8005)
XML External Entity injection. Leverage XML parsing vulnerabilities to read files or exfiltrate data.

### 🔍 Research Portal (Port 8006)
General web application challenge with mixed vulnerabilities. Information gathering and exploitation required.

### 🧠 Neural Guard (Port 8008)
Machine learning security challenge. Bypass or exploit AI-based detection/classification systems.

---

## 🚀 Getting Started

### TCP Challenges (Crypto/Misc)
```bash
nc chall.ch0wn3rs.ninja 8001    # LCG Oracle
nc chall.ch0wn3rs.ninja 8008    # Neural Guard
nc chall.ch0wn3rs.ninja 8009    # NebulaChat
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

---

## 📚 Infrastructure & Deployment

See [infra/README.md](infra/README.md) for:
- Architecture overview
- Deployment procedures
- Challenge updates
- Troubleshooting
- Infrastructure as Code (Bicep)

---

## 🗂️ Repository Structure

```
CTF-Marzo2/
├── AI/                          # Machine Learning challenges
│   ├── reto1_pickle_ai/
│   └── reto2_model_inversion/
├── crypto/                      # Cryptographic challenges
│   ├── reto1_lcg/              # LCG Oracle (Port 8001)
│   ├── reto3_nebulachat/       # NebulaChat (Port 8009)
│   └── reto4_mersenne/         # Mersenne Revenge (Port 8010)
├── web/                         # Web security challenges
│   ├── reto_jwt_confusion/     # JWT Confusion (Port 8002)
│   ├── reto_pkl_injection/     # Pickle Injection (Port 8003)
│   ├── reto_xss/               # XSS Challenge (Port 8004)
│   ├── reto_xxe/               # XXE Challenge (Port 8005)
│   ├── Web 1 - Research Portal # Research Portal (Port 8006)
│   └── Web 2 - Link Checker    # Link Checker (Port 8007)
├── Misc/
│   └── Misc 1 - Neural Guard   # Neural Guard (Port 8008)
├── docker-compose.yml           # Unified orchestration (10 services)
└── infra/
    ├── main.bicep              # Azure IaC template
    └── README.md               # Deployment documentation
```

---

## 📊 Status

- ✅ **10 Challenges Active** across 3 categories
- ✅ **Docker Containerized** with unified compose
- ✅ **Azure Deployed** (Standard_B2as_v2, Canada Central)
- ✅ **All Services Healthy** (verified)
- ⏱️ **Last Updated:** March 3, 2026

---

## 🔗 Quick Links

- **Main Website:** https://ch0wn3rs.ninja
- **Challenge Host:** chall.ch0wn3rs.ninja
- **SSH Access:** `ssh ctfadmin@chall.ch0wn3rs.ninja` (Authorized keys only)
- **Documentation:** [infra/README.md](infra/README.md)

---

*For infrastructure updates, maintenance procedures, or adding new challenges, see [infra/README.md](infra/README.md).*

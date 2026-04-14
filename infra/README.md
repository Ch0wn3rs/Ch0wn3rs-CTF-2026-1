# CTF-Marzo2 — Infrastructure Documentation

> **📋 For Participants:** See [../README.md](../README.md) for challenge descriptions, access instructions, and quick-start guides.

## Table of Contents

1. [Overview](#overview)
2. [Workflow Overview](#workflow-overview)
3. [Architecture](#architecture)
4. [Prerequisites](#prerequisites)
5. [Repository Structure](#repository-structure)
6. [Challenge Port Map](#challenge-port-map)
7. [Initial Deployment (From Scratch)](#initial-deployment-from-scratch)
8. [Updating Challenges](#updating-challenges)
9. [Tearing Down Infrastructure](#tearing-down-infrastructure)
10. [Local Development](#local-development)
11. [Troubleshooting](#troubleshooting)
12. [Security Considerations](#security-considerations)
13. [Cost Estimates](#cost-estimates)
14. [Reference: Bicep Parameters](#reference-bicep-parameters)

---

## Overview

This repository contains the CTF challenges for **CTF-Marzo2**, organized by category (crypto, web, stego, forensics, AI). All challenges that have network services are containerized with Docker and deployed as a single unit to an **Azure Virtual Machine** using a **Bicep** Infrastructure-as-Code template.

The deployment model is:

1. Challenge code is packaged into a **tarball** and uploaded to **Azure Blob Storage**.
2. A **Bicep template** provisions a VM with cloud-init that automatically installs Docker, downloads the tarball, and runs `docker compose up -d --build`.
3. All 10 network challenges (3 crypto + 5 web + 2 misc) run as background daemons on ports 8001–8010.

---

## Workflow Overview

**Participant-Facing Documentation:**  
See [../README.md](../README.md) for challenge descriptions, access information, and quick-start instructions.

**Infrastructure Operations:**  
This document covers deployment, updates, scaling, and maintenance of the cloud infrastructure.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Azure – Canada Central                                 │
│                                                         │
│  ┌─────────────────────────────────────────────────┐    │
│  │  Resource Group: ctf-marzo2-rg                  │    │
│  │                                                 │    │
│  │  ┌──────────────┐   ┌────────────────────────┐  │    │
│  │  │  Storage Acct │   │  VM: ctf-marzo2-vm     │  │    │
│  │  │  ctfmarzo2sa  │──▶│  Standard_B2as_v2      │  │    │
│  │  │  (tarball)    │   │  Ubuntu 22.04 LTS      │  │    │
│  │  └──────────────┘   │  2 vCPUs / 8 GB RAM     │  │    │
│  │                      │                          │  │    │
│  │                      │  Docker Compose (10 svc): │  │    │
│  │                      │   ├─ lcg_oracle    :8001 │  │    │
│  │                      │   ├─ jwt_confusion :8002 │  │    │
│  │                      │   ├─ pkl_injection :8003 │  │    │
│  │                      │   ├─ xss_challenge :8004 │  │    │
│  │                      │   ├─ xxe_challenge :8005 │  │    │
│  │                      │   ├─ web1_portal   :8006 │  │    │
│  │                      │   ├─ web2_checker  :8007 │  │    │
│  │                      │   ├─ neural_guard  :8008 │  │    │
│  │                      │   ├─ nebulachat    :8009 │  │    │
│  │                      │   └─ mersenne      :8010 │  │    │
│  │                      └────────────────────────┘  │    │
│  │                                                 │    │
│  │  NSG Rules: SSH 22, Challenges 8001-8010        │    │
│  │  Public IP: Static                              │    │
│  │  VNet: 10.0.0.0/16                              │    │
│  └─────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────┘
```

### Azure Resources Created

| Resource | Name | Purpose |
|---|---|---|
| Resource Group | `ctf-marzo2-rg` | Logical container for all resources |
| Storage Account | `ctfmarzo2sa` | Hosts the CTF tarball for VM download |
| Virtual Machine | `ctf-marzo2-vm` | Runs all Docker containers |
| Public IP | `ctf-marzo2-vm-pip` | Static IP for external access |
| NIC | `ctf-marzo2-vm-nic` | Network interface for the VM |
| NSG | `ctf-marzo2-vm-nsg` | Firewall rules (SSH + challenge ports) |
| VNet | `ctf-marzo2-vm-vnet` | Virtual network (10.0.0.0/16) |
| OS Disk | `ctf-marzo2-vm-osdisk` | 30 GB Premium SSD |

---

## Prerequisites

### Tools

| Tool | Version | Purpose |
|---|---|---|
| Azure CLI (`az`) | ≥ 2.50 | Deploy infrastructure |
| Bicep CLI | ≥ 0.20 (bundled with `az`) | Compile IaC templates |
| Docker & Docker Compose | ≥ 24.x / v2 | Local testing |
| `curl` | any | Endpoint testing |
| `nc` (netcat) | any | TCP challenge testing |

### Azure Access

- An active Azure subscription (e.g., "Azure for Students").
- Authenticated via `az login`. If MFA is required:

  ```bash
  az logout
  az login --tenant "<TENANT_ID>" --scope "https://management.core.windows.net//.default"
  ```

- Sufficient **vCPU quota** in the target region. The `Standard_B2as_v2` VM requires **2 cores**. Check current usage:

  ```bash
  az vm list-usage --location canadacentral \
    --query "[?localName=='Total Regional vCPUs'].{used:currentValue, limit:limit}" \
    -o table
  ```

---

## Repository Structure

```
CTF-Marzo2/
├── docker-compose.yml          # Unified compose for all challenges
├── infra/
│   └── main.bicep              # Azure Bicep IaC template
├── crypto/
│   ├── reto1_lcg/              # LCG Oracle (TCP :1337)
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml  # Individual compose (for local dev)
│   │   ├── server.py
│   │   └── flag.txt
│   └── reto2_aes/              # AES challenge (offline, no Docker)
├── web/
│   ├── reto_jwt_confusion/     # JWT Confusion (HTTP :5000)
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── app.py
│   │   └── ...
│   ├── reto_pkl_injection/     # Pickle Injection (HTTP :5000)
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   ├── app.py
│   │   └── ...
│   ├── reto_xss/               # XSS Challenge (HTTP :5000)
│   │   ├── Dockerfile
│   │   ├── docker-compose.yml
│   │   └── app.py
│   └── reto_xxe/               # XXE Challenge (HTTP :5001)
│       ├── Dockerfile
│       ├── docker-compose.yml
│       ├── app.py
│       └── ...
├── AI/                         # AI challenges (offline)
├── Stego/                      # Steganography challenges (offline)
└── forense/                    # Forensics challenges (offline)
```

> **Note:** Only challenges with a `Dockerfile` are deployed to the VM. Offline challenges (AI, Stego, Forensics, crypto/reto2_aes) are distributed separately.

---

## Challenge Port Map

**Production Hostname:** `chall.ch0wn3rs.ninja`

| # | Category | Challenge | Host Port | Access |
|---|---|---|---|---|
| 1 | Crypto | LCG Oracle | **8001** | `nc chall.ch0wn3rs.ninja 8001` |
| 2 | Web | JWT Confusion | **8002** | `http://chall.ch0wn3rs.ninja:8002` |
| 3 | Web | Pickle Injection | **8003** | `http://chall.ch0wn3rs.ninja:8003` |
| 4 | Web | XSS Challenge | **8004** | `http://chall.ch0wn3rs.ninja:8004` |
| 5 | Web | XXE Challenge | **8005** | `http://chall.ch0wn3rs.ninja:8005` |
| 6 | Web | Research Portal | **8006** | `http://chall.ch0wn3rs.ninja:8006` |
| 7 | Web | Link Checker | **8007** | `http://chall.ch0wn3rs.ninja:8007` |
| 8 | Misc | Neural Guard | **8008** | `nc chall.ch0wn3rs.ninja 8008` |
| 9 | Crypto | NebulaChat | **8009** | `nc chall.ch0wn3rs.ninja 8009` |
| 10 | Crypto | Mersenne Revenge | **8010** | `nc chall.ch0wn3rs.ninja 8010` |

---

## Initial Deployment (From Scratch)

### Step 1 — Authenticate with Azure

```bash
az login
# If MFA is required:
az login --tenant "<TENANT_ID>" --scope "https://management.core.windows.net//.default"
```

### Step 2 — Create the Resource Group

```bash
az group create --name ctf-marzo2-rg --location canadacentral
```

### Step 3 — Create the Storage Account and Upload the Tarball

```bash
# Create storage account with public blob access
az storage account create \
  --name ctfmarzo2sa \
  --resource-group ctf-marzo2-rg \
  --location canadacentral \
  --sku Standard_LRS \
  --kind StorageV2 \
  --allow-blob-public-access true

# Create a public blob container
az storage container create \
  --name deploy \
  --account-name ctfmarzo2sa \
  --public-access blob

# Package the repo (excluding .git and caches)
tar czf /tmp/ctf-marzo2.tar.gz \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='infra/main.json' \
  .

# Upload
az storage blob upload \
  --account-name ctfmarzo2sa \
  --container-name deploy \
  --name ctf-marzo2.tar.gz \
  --file /tmp/ctf-marzo2.tar.gz \
  --overwrite
```

### Step 4 — Deploy the Bicep Template

```bash
az deployment group create \
  --resource-group ctf-marzo2-rg \
  --template-file infra/main.bicep \
  --parameters \
    adminUsername=ctfadmin \
    adminPasswordOrKey='<STRONG_PASSWORD>' \
    authenticationType=password
```

> **Password requirements:** 12-72 characters, must include uppercase, lowercase, digit, and special character.

The deployment takes ~2 minutes for provisioning + ~3-5 minutes for cloud-init (Docker install + image builds).

### Step 5 — Retrieve the Public IP

```bash
az deployment group show \
  --resource-group ctf-marzo2-rg \
  --name main \
  --query 'properties.outputs' \
  -o json
```

Example output:
```json
{
  "vmPublicIp": { "value": "20.48.236.232" },
  "sshCommand": { "value": "ssh ctfadmin@20.48.236.232" },
  "challengeUrls": {
    "value": {
      "crypto_lcg": "nc 20.48.236.232 8001",
      "web_jwt_confusion": "http://20.48.236.232:8002",
      "web_pkl_injection": "http://20.48.236.232:8003",
      "web_xss": "http://20.48.236.232:8004",
      "web_xxe": "http://20.48.236.232:8005"
    }
  }
}
```

### Step 6 — Verify Deployment

Wait ~5 minutes after the deployment finishes, then test:

```bash
IP="20.48.236.232"  # Replace with your IP

# Test TCP challenge
echo "" | nc -w3 $IP 8001

# Test HTTP challenges
for port in 8002 8003 8004 8005; do
  curl -s -o /dev/null -w "Port $port: HTTP %{http_code}\n" \
    --connect-timeout 5 http://$IP:$port/
done
```

Or check via `az vm run-command` (no SSH needed):

```bash
az vm run-command invoke \
  --resource-group ctf-marzo2-rg \
  --name ctf-marzo2-vm \
  --command-id RunShellScript \
  --scripts "cloud-init status; docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'" \
  --query 'value[0].message' -o tsv
```

---

## Updating Challenges

> ⚠️ **IMPORTANT — NEVER DELETE THE VM DURING A NORMAL UPDATE.**
> Deleting the VM changes the public IP, breaks DNS, and causes unnecessary downtime.
> VM deletion belongs **only** in the [Tearing Down Infrastructure](#tearing-down-infrastructure) section.
> All routine deployments — including adding/removing challenges or fixing flags — use the
> **in-place update procedure (Option A)** below.

When you modify challenge code (e.g., fix a bug, change a flag, add/remove a challenge), follow
this workflow:

### Option A — In-Place Update via `az vm run-command` ✅ Standard procedure

Use this for **all** updates: bug fixes, flag changes, adding/removing services, port map changes.
The VM stays up; the public IP and DNS are unaffected.

```bash
# 1. Package updated code
cd /path/to/CTF-Marzo2
tar czf /tmp/ctf-marzo2.tar.gz \
  --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='node_modules' --exclude='*.tar.gz' \
  .

# 2. Upload new tarball
az storage blob upload \
  --account-name ctfmarzo2sa \
  --container-name deploy \
  --name ctf-marzo2.tar.gz \
  --file /tmp/ctf-marzo2.tar.gz \
  --overwrite

# 3. Apply changes on the running VM (no SSH needed)
az vm run-command invoke \
  --resource-group ctf-marzo2-rg \
  --name ctf-marzo2-vm \
  --command-id RunShellScript \
  --scripts "
    set -e
    curl -fsSL https://ctfmarzo2sa.blob.core.windows.net/deploy/ctf-marzo2.tar.gz \
      -o /tmp/ctf-marzo2.tar.gz
    rm -rf /opt/ctf-marzo2/*
    tar xzf /tmp/ctf-marzo2.tar.gz -C /opt/ctf-marzo2
    cd /opt/ctf-marzo2
    docker compose down
    docker compose up -d --build
  " \
  --query 'value[0].message' -o tsv
```

Or via SSH if you prefer:

```bash
IP="<VM_PUBLIC_IP>"
ssh ctfadmin@$IP "
  sudo bash -c '
    curl -fsSL https://ctfmarzo2sa.blob.core.windows.net/deploy/ctf-marzo2.tar.gz \
      -o /tmp/ctf-marzo2.tar.gz &&
    rm -rf /opt/ctf-marzo2/* &&
    tar xzf /tmp/ctf-marzo2.tar.gz -C /opt/ctf-marzo2 &&
    cd /opt/ctf-marzo2 &&
    docker compose down &&
    docker compose up -d --build
  '
"
```

### Option B — Update a Single Challenge (fastest)

If only one challenge changed, rebuild just that service on the running VM:

```bash
az vm run-command invoke \
  --resource-group ctf-marzo2-rg \
  --name ctf-marzo2-vm \
  --command-id RunShellScript \
  --scripts "cd /opt/ctf-marzo2 && docker compose up -d --build <service_name>" \
  --query 'value[0].message' -o tsv
```

Service names: `lcg_oracle`, `jwt_confusion`, `pkl_injection`, `xss_challenge`, `xxe_challenge`,
`web1_research_portal`, `web2_link_checker`, `misc1_neural_guard`, `mersenne_revenge`.

### Option C — Full From-Scratch Redeploy ⚠️ Avoid during active CTF

**Only use this if the VM itself is broken/gone or infra changes require it (e.g., new ports, new
NSG rules, new VM size).** This changes the public IP — update DNS afterwards.

See [Tearing Down Infrastructure](#tearing-down-infrastructure) to delete the old VM first, then
follow [Initial Deployment (From Scratch)](#initial-deployment-from-scratch) to recreate it.

---

## Tearing Down Infrastructure

### Delete Everything

```bash
az group delete --name ctf-marzo2-rg --yes --no-wait
```

This removes **all** resources in the resource group (VM, storage, networking) in one command.

### Delete Only the VM (Keep Storage)

```bash
az vm delete --name ctf-marzo2-vm \
  --resource-group ctf-marzo2-rg --yes --force-deletion true

# Clean up orphaned resources
az disk delete --name ctf-marzo2-vm-osdisk \
  --resource-group ctf-marzo2-rg --yes --no-wait
az network nic delete --name ctf-marzo2-vm-nic \
  --resource-group ctf-marzo2-rg --no-wait
sleep 30
az network public-ip delete --name ctf-marzo2-vm-pip \
  --resource-group ctf-marzo2-rg --no-wait
```

### Deallocate VM (Stop Billing, Keep State)

To temporarily stop the VM without deleting it:

```bash
az vm deallocate --name ctf-marzo2-vm --resource-group ctf-marzo2-rg
```

To start it again:

```bash
az vm start --name ctf-marzo2-vm --resource-group ctf-marzo2-rg
```

> **Note:** The public IP remains allocated (and billed) while the VM is deallocated. To avoid IP charges, delete the public IP separately.

---

## Local Development

### Run All Challenges Locally

From the repository root:

```bash
docker compose up -d --build
```

Challenges will be available at `localhost:8001`–`localhost:8005`.

### Run a Single Challenge Locally

Each challenge directory has its own `docker-compose.yml` for isolated testing:

```bash
cd web/reto_xss
docker compose up -d --build
# Available at the port defined in that challenge's compose file
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f jwt_confusion
```

### Rebuild After Changes

```bash
docker compose up -d --build <service_name>
```

---

## Troubleshooting

### Cloud-init didn't finish / containers aren't running

Check cloud-init status from your local machine:

```bash
az vm run-command invoke \
  --resource-group ctf-marzo2-rg \
  --name ctf-marzo2-vm \
  --command-id RunShellScript \
  --scripts "cloud-init status; tail -50 /var/log/cloud-init-output.log" \
  --query 'value[0].message' -o tsv
```

- `status: running` → still in progress, wait a few more minutes.
- `status: error` → check the log output for errors.
- `status: done` → cloud-init finished; check Docker: `docker ps -a`.

### Containers are crashing

```bash
az vm run-command invoke \
  --resource-group ctf-marzo2-rg \
  --name ctf-marzo2-vm \
  --command-id RunShellScript \
  --scripts "cd /opt/ctf-marzo2 && docker compose ps -a && docker compose logs --tail=30" \
  --query 'value[0].message' -o tsv
```

### Port not reachable from outside

1. **Check NSG rules** — ports 8001-8005 must be allowed:
   ```bash
   az network nsg rule list --nsg-name ctf-marzo2-vm-nsg \
     --resource-group ctf-marzo2-rg -o table
   ```
2. **Check the container is listening:**
   ```bash
   az vm run-command invoke \
     --resource-group ctf-marzo2-rg \
     --name ctf-marzo2-vm \
     --command-id RunShellScript \
     --scripts "ss -tlnp | grep -E '800[1-5]'" \
     --query 'value[0].message' -o tsv
   ```

### VM quota exceeded

```
QuotaExceeded: ... Total Regional Cores quota ...
```

- List current VMs: `az vm list -o table`
- Delete unused VMs or request a quota increase via the Azure Portal.
- Alternatively, deploy to a different region by passing `--parameters location=eastus`.

### Bicep compilation errors

```bash
az bicep build --file infra/main.bicep
```

The `no-hardcoded-env-urls` warning about `core.windows.net` is expected and can be safely ignored — it refers to the default tarball URL parameter.

### SSH into the VM

```bash
ssh ctfadmin@<PUBLIC_IP>
# Password: the one provided during deployment
```

---

## Security Considerations

### Current Setup (CTF Event)

This deployment is designed for a **short-lived CTF event**, not for production workloads. The following trade-offs were made intentionally:

| Item | Current State | Recommendation for Production |
|---|---|---|
| SSH access | Open to `*` (any IP) | Restrict `sourceAddressPrefix` to organizer IPs |
| Authentication | Password-based | Use SSH public keys (`authenticationType=sshPublicKey`) |
| Blob storage | Public read access | Use SAS tokens with expiry |
| HTTPS | Not configured | Add a reverse proxy (nginx/Caddy) with Let's Encrypt |
| Flags | Hardcoded in images | Inject via environment variables or secrets |
| VM admin password | Passed as CLI param | Use Azure Key Vault references |
| Challenge isolation | Shared Docker host | Use separate VMs or container groups |

### Hardening for Longer Deployments

1. **Restrict SSH** — Edit the NSG rule to allow only your IP:
   ```bash
   az network nsg rule update \
     --nsg-name ctf-marzo2-vm-nsg \
     --resource-group ctf-marzo2-rg \
     --name Allow-SSH \
     --source-address-prefixes "<YOUR_IP>/32"
   ```

2. **Use SSH keys instead of passwords:**
   ```bash
   az deployment group create \
     --resource-group ctf-marzo2-rg \
     --template-file infra/main.bicep \
     --parameters \
       adminUsername=ctfadmin \
       adminPasswordOrKey="$(cat ~/.ssh/id_rsa.pub)" \
       authenticationType=sshPublicKey
   ```

3. **Auto-shutdown** to save costs:
   ```bash
   az vm auto-shutdown \
     --resource-group ctf-marzo2-rg \
     --name ctf-marzo2-vm \
     --time 2300 \
     --timezone "Eastern Standard Time"
   ```

---

## Cost Estimates

| Resource | SKU | Estimated Cost (USD/month) |
|---|---|---|
| VM (Standard_B2as_v2) | 2 vCPU, 8 GB, burstable | ~$44 |
| OS Disk (Premium SSD) | 30 GB P4 | ~$5 |
| Public IP (Standard) | Static | ~$4 |
| Storage Account (LRS) | ~4 MB stored | < $0.01 |
| **Total** | | **~$53/month** |

> **Tip:** Deallocate the VM when not in use (`az vm deallocate ...`) to stop compute charges. Only disk and IP charges remain (~$9/month).

---

## Reference: Bicep Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `adminUsername` | string | `ctfadmin` | VM admin user |
| `adminPasswordOrKey` | secureString | *(required)* | Password or SSH public key |
| `authenticationType` | string | `password` | `password` or `sshPublicKey` |
| `tarballUrl` | string | `https://ctfmarzo2sa.blob.core.windows.net/deploy/ctf-marzo2.tar.gz` | URL of the CTF code tarball |
| `location` | string | `canadacentral` | Azure region |
| `vmSize` | string | `Standard_B2as_v2` | VM size (2 vCPU, 8 GB) |

### Deployment Outputs

| Output | Description |
|---|---|
| `vmPublicIp` | The static public IP address of the VM |
| `sshCommand` | Ready-to-use SSH command |
| `challengeUrls` | Object with connection strings for each challenge |

---

## Adding a New Challenge

1. Create a directory under the appropriate category (e.g., `web/reto_new/`).
2. Add a `Dockerfile` and optionally a standalone `docker-compose.yml`.
3. Add the service to the root `docker-compose.yml`:
   ```yaml
   new_challenge:
     build: ./web/reto_new
     ports:
       - "8009:5000"       # Use the next available port
     restart: unless-stopped
   ```
4. Update the NSG rule in `infra/main.bicep` to include the new port:
   ```
   destinationPortRange: '8001-8009'    # was 8001-8008
   ```
5. Add the new URL to the Bicep outputs section.
6. Follow the [Updating Challenges](#updating-challenges) workflow to deploy.

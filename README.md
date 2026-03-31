<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-6.0-47A248?logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/Celery-5.x-37814A?logo=celery&logoColor=white" />
  <img src="https://img.shields.io/badge/Tor-SOCKS5-7D4698?logo=torproject&logoColor=white" />
  <img src="https://img.shields.io/badge/HuggingFace-NLP-FFD21E?logo=huggingface&logoColor=black" />
  <img src="https://img.shields.io/badge/license-MIT-green" />
</p>

# DarkIntelliWeb — AI-Powered Dark Web Threat Intelligence Platform

**DarkIntelliWeb** is an enterprise-grade, end-to-end cybersecurity threat intelligence platform that autonomously crawls dark web `.onion` services, classifies threats using state-of-the-art NLP models, extracts and enriches Indicators of Compromise (IOCs), calculates risk scores, and visualizes actionable intelligence through a real-time SOC dashboard.

> Built for security researchers, SOC analysts, and CTI teams who need automated, continuous dark web monitoring without manual intervention.

---

## Table of Contents

- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Reference](#api-reference)
- [Dashboard](#dashboard)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)
- [License](#license)

---

## Key Features

| Capability | Description |
|---|---|
| **Autonomous Dark Web Crawling** | Async crawler routes through Tor SOCKS5 proxy, respects depth limits, and deduplicates pages before storage. |
| **AI Threat Classification** | Zero-shot classification via HuggingFace (`distilbart-mnli-12-3`) categorizes content into 9+ threat categories with confidence scoring. Falls back to keyword heuristics if the model is unavailable. |
| **IOC Extraction** | Regex-based extraction of IPs, emails, crypto wallets, domains, MD5 hashes, and SHA-256 hashes from crawled content. |
| **Live Threat Enrichment** | Real-time enrichment via **VirusTotal v3** and **AbuseIPDB v2** APIs with parallel async requests and graceful fallback. |
| **Risk Scoring Engine** | Configurable weighted scoring combining AI confidence, category severity, and indicator criticality into a 0–100 risk score. |
| **Threat Correlation Graph** | NetworkX-powered intelligence graph mapping relationships between sources, categories, and indicators, visualized with Plotly. |
| **Enterprise SOC Dashboard** | 8-page Streamlit dashboard with threat overview, explorer, IOC repository, intelligence graph, global threat map, analytics, target management, and engine settings. |
| **Scheduled Automation** | Celery Beat schedules crawl cycles (default: every 6 hours), with on-demand manual scans via the dashboard or API. |
| **Alerting** | Automatic `CRITICAL` / `HIGH` alerts generated when risk scores exceed configurable thresholds. |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Docker Compose                           │
│                                                                 │
│  ┌─────────┐    ┌───────────┐    ┌──────────┐    ┌───────────┐ │
│  │   Tor   │◄───│  Crawler  │───►│ MongoDB  │◄───│  FastAPI   │ │
│  │  Proxy  │    │  (async)  │    │  (Motor) │    │  Backend   │ │
│  └─────────┘    └─────┬─────┘    └────┬─────┘    └─────┬─────┘ │
│                       │               │                │       │
│                 ┌─────▼─────┐         │          ┌─────▼─────┐ │
│                 │  Celery   │─────────┘          │ Streamlit │ │
│                 │  Worker   │                    │ Dashboard │ │
│                 └─────┬─────┘                    └───────────┘ │
│                       │                                        │
│         ┌─────────────┼─────────────┐                          │
│         │             │             │                          │
│   ┌─────▼───┐   ┌─────▼───┐  ┌─────▼──────┐                  │
│   │   AI    │   │   IOC   │  │  Threat    │                   │
│   │ Engine  │   │Extractor│  │ Enrichment │                   │
│   │  (NLP)  │   │ (Regex) │  │ (VT/Abuse) │                   │
│   └─────────┘   └─────────┘  └────────────┘                   │
│                                                                 │
│  ┌─────────┐                                                   │
│  │  Redis  │ ◄── Celery Broker                                 │
│  └─────────┘                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI + Uvicorn |
| Database | MongoDB 6 (Motor async driver) |
| Task Queue | Celery 5 + Redis 7 |
| Crawler | aiohttp + aiohttp-socks (Tor SOCKS5) |
| AI/NLP | HuggingFace Transformers (DistilBART) |
| Enrichment | VirusTotal v3 API, AbuseIPDB v2 API |
| Graph Analysis | NetworkX |
| Dashboard | Streamlit + Plotly |
| Containerization | Docker Compose |
| Frontend (Optional) | React + Vite + TypeScript + TailwindCSS |

---

## Project Structure

```
DarkIntelliWeb/
├── api/                          # FastAPI application
│   ├── main.py                   # App entrypoint & CORS config
│   └── routes.py                 # REST endpoints (/overview, /threats, /alerts, /graph, /targets, /scan)
├── ai_engine/
│   └── classifier.py             # Zero-shot NLP classification with keyword fallback
├── config/
│   ├── config.yaml               # Global configuration (proxy, scoring weights, API keys, severity map)
│   ├── loader.py                 # YAML/JSON config loaders
│   ├── logger.py                 # Centralized logging setup
│   └── targets.json              # Active .onion crawl targets
├── crawler/
│   └── scraper.py                # Async dark web crawler with Tor proxy support
├── dashboard/
│   ├── app.py                    # 8-page Streamlit SOC dashboard
│   └── Dockerfile
├── database/
│   ├── db.py                     # Motor async + PyMongo sync database clients
│   └── models.py                 # Pydantic data models
├── frontend/                     # React + Vite + TypeScript frontend (optional)
│   └── src/
├── ioc_extractor/
│   └── extractor.py              # Regex-based IOC extraction (IP, email, crypto, hash, domain)
├── risk_scoring/
│   └── scorer.py                 # Weighted risk score calculation engine
├── scheduler/
│   ├── celery_app.py             # Celery + Redis configuration with beat schedule
│   └── tasks.py                  # Crawling pipeline orchestration task
├── threat_intelligence/
│   ├── correlation.py            # NetworkX threat graph generation
│   └── enrichment.py             # Live enrichment via VirusTotal & AbuseIPDB APIs
├── utils/
│   └── sample_data.py            # Seed script for demo/test data
├── backend/
│   └── Dockerfile
├── docker-compose.yml            # Full stack orchestration (6 services)
├── requirements.txt
├── LICENSE
└── README.md
```

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- (Optional) VirusTotal and AbuseIPDB API keys for live enrichment

### 1. Clone the Repository

```bash
git clone https://github.com/Shivanshtripathi03/DarkIntelliWeb.git
cd DarkIntelliWeb
```

### 2. Configure API Keys (Optional)

Edit `config/config.yaml` to add your enrichment API keys:

```yaml
apis:
  abuseipdb: "YOUR_ABUSEIPDB_API_KEY"
  virustotal: "YOUR_VIRUSTOTAL_API_KEY"
```

> If left empty, the system gracefully falls back to default values (0 detections) — the pipeline will not crash.

### 3. Build & Launch

```bash
docker-compose up --build -d
```

This starts **6 services**:

| Service | Port | Purpose |
|---|---|---|
| `tor` | 9050 | SOCKS5 proxy for `.onion` routing |
| `mongodb` | 27017 | Intelligence database |
| `redis` | 6379 | Celery message broker |
| `backend` | 8000 | FastAPI REST API |
| `celery_worker` | — | Background crawling & analysis |
| `dashboard` | 8501 | Streamlit SOC dashboard |

### 4. Access the Dashboard

Open your browser to **[http://localhost:8501](http://localhost:8501)**.

### 5. Add Crawl Targets

Navigate to the **Crawler Targets** tab in the dashboard and add `.onion` URLs. The system picks them up automatically on the next Celery beat cycle (every 6 hours by default), or trigger an immediate scan via the **Run Manual Scan** button.

### 6. Seed Sample Data (Optional)

```bash
docker-compose exec backend python utils/sample_data.py
```

---

## Configuration

All configuration is centralized in `config/config.yaml`:

```yaml
crawler:
  proxy: socks5://tor:9150        # Tor SOCKS5 proxy endpoint
  crawl_interval_minutes: 360     # Celery beat schedule
  max_depth: 2                    # Link-following depth
  timeout_seconds: 60             # Per-request timeout

scoring:
  high_risk_threshold: 70         # Alert threshold (0-100)
  weights:
    ai_confidence: 0.4            # NLP confidence weight
    category_severity: 0.4        # Category severity weight
    indicator_criticality: 0.2    # IOC criticality weight

apis:
  abuseipdb: ""                   # AbuseIPDB v2 API key
  virustotal: ""                  # VirusTotal v3 API key

categories_severity:              # Severity scores per threat category
  "data breaches": 90
  "ransomware activity": 95
  "malware marketplaces": 85
  # ... (see config.yaml for full list)
```

Settings can also be modified at runtime via the **Settings** page in the dashboard.

---

## API Reference

Base URL: `http://localhost:8000/api`

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/overview` | Dashboard summary (total threats, alerts, category breakdown) |
| `GET` | `/threats?limit=50&skip=0` | Paginated threat logs sorted by timestamp |
| `GET` | `/alerts?limit=10` | Recent alert feed |
| `GET` | `/graph` | Threat correlation graph (NetworkX node-link format) |
| `GET` | `/targets` | List active crawl targets |
| `POST` | `/targets` | Add a new crawl target (`{"url": "http://...onion"}`) |
| `DELETE` | `/targets` | Remove a crawl target (`{"url": "http://...onion"}`) |
| `POST` | `/scan` | Trigger an immediate crawl cycle |

---

## Dashboard

The Streamlit dashboard provides **8 pages** for comprehensive threat intelligence operations:

1. **Threat Overview** — KPI metrics, category donut chart, risk distribution histogram, latest high-risk detections table
2. **Threat Explorer** — Full-text search, risk/category filters, detailed threat payload viewer with content snippets and IOC tables
3. **Indicators of Compromise** — Sortable/filterable IOC repository with enrichment metadata (country, ISP, reputation, malware detections)
4. **Threat Intelligence Graph** — Interactive Plotly network graph visualizing URL → Category → IOC relationships
5. **Global Threat Map** — Choropleth map showing geospatial distribution of threat infrastructure
6. **Threat Analytics** — Category trend lines over time, top malicious domains/IPs bar chart
7. **Crawler Targets** — Add/remove `.onion` targets, trigger manual scans
8. **Settings** — Runtime configuration for scoring thresholds, crawl intervals, proxy settings, and API keys

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Disclaimer

> **⚠️ This tool is intended strictly for authorized security research, academic study, and lawful threat intelligence operations.** Unauthorized access to computer systems is illegal. Users are solely responsible for ensuring compliance with all applicable local, state, national, and international laws. The authors assume no liability for misuse.

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <b>Built with ❤️ by <a href="https://github.com/Shivanshtripathi03">Shivansh Tripathi</a></b>
</p>

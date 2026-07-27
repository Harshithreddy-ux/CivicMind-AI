<div align="center">

<img src="assets/logo.svg" width="120" alt="CivicMind AI Logo"/>

# CivicMind AI

### Enterprise Smart City Decision Intelligence Platform

*Multi-Agent AI · Real-Time GIS · Disaster Analytics · Urban Decision Support*

---

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=flat-square&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)](https://ai.google.dev)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Last Commit](https://img.shields.io/github/last-commit/Harshithreddy-ux/CivicMind-AI?style=flat-square)](https://github.com/Harshithreddy-ux/CivicMind-AI/commits/main)
[![Stars](https://img.shields.io/github/stars/Harshithreddy-ux/CivicMind-AI?style=flat-square)](https://github.com/Harshithreddy-ux/CivicMind-AI/stargazers)
[![Forks](https://img.shields.io/github/forks/Harshithreddy-ux/CivicMind-AI?style=flat-square)](https://github.com/Harshithreddy-ux/CivicMind-AI/network/members)
[![Issues](https://img.shields.io/github/issues/Harshithreddy-ux/CivicMind-AI?style=flat-square)](https://github.com/Harshithreddy-ux/CivicMind-AI/issues)

**[Live Demo](https://civicmind-x8zrh8o23aahmfrymvd52j.streamlit.app) · [Documentation](docs/) · [Report Bug](https://github.com/Harshithreddy-ux/CivicMind-AI/issues) · [Request Feature](https://github.com/Harshithreddy-ux/CivicMind-AI/issues)**

</div>

---

## What is CivicMind AI?

CivicMind AI is a production-grade **Smart City Decision Intelligence Platform** that helps city administrators, emergency responders, and urban planners make faster, better-informed decisions using real-time data.

Instead of a conventional dashboard, CivicMind AI uses a **Multi-Agent AI Architecture** — specialized Gemini-powered agents work in parallel to analyze weather, air quality, crime patterns, hospital capacity, and flood risk before synthesizing a final actionable recommendation.

> **Built for Hack2Skill, deployed on Streamlit Community Cloud, and open for contributions.**

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **Multi-Agent AI** | Parallel domain agents (Weather, AQI, Crime, Hospital, Flood) collaborating via Supervisor orchestration |
| 🌦 **Real-Time Weather & AQI** | Live telemetry via Open-Meteo & WAQI APIs with async HTTPX client |
| 🗺 **GIS City Intelligence** | Folium maps with clustered hospital markers, flood zones, and AQI overlays |
| 📊 **Analytics Dashboard** | Plotly-powered charts with animated transitions and CSV/PNG export |
| 🔮 **7-Day Forecast** | Temperature, humidity, and AQI trend projections |
| 📋 **Municipal Reports** | One-click export in Markdown, CSV, and JSON |
| 🧠 **RAG Decision Engine** | Retrieval-Augmented Generation over municipal SOP guidelines |
| 🗄 **SQLite Data Layer** | 32,000+ hospital records indexed for sub-millisecond queries |
| 🔒 **Graceful Fallbacks** | Every API failure handled silently — app never crashes |

---

## 📸 Screenshots

<details>
<summary><b>Click to expand screenshots</b></summary>

### 🏠 Home — Landing Page
> Animated hero with real metrics, technology showcase, and architecture overview.

### 📊 Dashboard
> Live weather, AQI, risk score, and city status cards with real-time telemetry.

### 🗺 City Intelligence — GIS Map
> Interactive Folium map with hospital clusters, flood overlays, and marker tooltips.

### 📈 Analytics
> Historical trend charts for crime, population, rainfall, and temperature.

### 🔮 Forecast
> 7-day multi-metric weather and AQI projections rendered as animated Plotly charts.

### 🧠 AI Assistant
> Gemini-powered conversational interface with source attribution and confidence scoring.

### 📋 Reports
> Downloadable executive reports with base64-encoded anchor buttons.

</details>

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    STREAMLIT FRONTEND                        │
│  Home · Dashboard · Analytics · City Intelligence           │
│  Forecast · AI Assistant · Reports · Settings               │
└─────────────────────┬───────────────────────────────────────┘
                      │  HTTP / Direct Import Fallback
┌─────────────────────▼───────────────────────────────────────┐
│                   FASTAPI BACKEND (port 8000)                │
│  /api/weather  /api/aqi  /api/analysis  /api/hospitals       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              SUPERVISOR AGENT ROUTER                         │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌───────────────┐  │
│  │ Weather  │ │  AQI     │ │  Crime   │ │   Hospital    │  │
│  │  Agent   │ │  Agent   │ │  Agent   │ │    Agent      │  │
│  └──────────┘ └──────────┘ └──────────┘ └───────────────┘  │
│  ┌──────────┐ ┌────────────────────────────────────────┐    │
│  │  Flood   │ │         Decision Agent (Gemini 2.5)    │    │
│  │  Agent   │ │    + RAG SOP Index (FAISS + Embeddings)│    │
│  └──────────┘ └────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    DATA LAYER                                │
│  SQLite (32k+ hospitals · crime · flood · population)        │
│  External APIs: Open-Meteo · WAQI · OpenStreetMap            │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧑‍💻 Agent System

| Agent | Domain | Data Sources |
|---|---|---|
| **Supervisor** | Task Routing & Orchestration | All agents |
| **Coordinator** | Parallel Execution Control | All agents |
| **Weather Agent** | Temperature, Wind, Humidity | Open-Meteo API |
| **AQI Agent** | Air Quality Index, PM2.5 | WAQI API |
| **Flood Agent** | Flood events, Rainfall, Catchment | IndoFlood DB, IMD Rainfall |
| **Crime Agent** | Crime patterns, Incident mapping | Crime Dataset India |
| **Hospital Agent** | Healthcare capacity, Accessibility | Hospital Directory (32k+) |
| **Decision Agent** | Final synthesis + Recommendations | Gemini 2.5 Flash + RAG |

---

## 🛠 Technology Stack

```
Frontend        │  Streamlit 1.30+, Plotly, Folium, HTML/CSS
Backend         │  FastAPI, Uvicorn, Pydantic v2, AsyncIO
AI / ML         │  Google Gemini 2.5 Flash, FAISS, RAG Pipeline
Database        │  SQLite 3 (indexed, 32k+ records)
HTTP Client     │  HTTPX AsyncClient
Mapping         │  Folium, OpenStreetMap, streamlit-folium
Testing         │  Pytest, pytest-asyncio
Data Science    │  Pandas, NumPy, GeoPandas
Config          │  python-dotenv, Pydantic Settings
CI/CD           │  GitHub Actions
Deployment      │  Streamlit Community Cloud
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- A [Google AI Studio](https://aistudio.google.com) API key (free)

### 1. Clone

```bash
git clone https://github.com/Harshithreddy-ux/CivicMind-AI.git
cd CivicMind-AI
```

### 2. Set up environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_key_here
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run (choose one)

**Option A — Backend + Frontend (full stack)**
```bash
# Terminal 1
uvicorn backend.main:app --reload --port 8000

# Terminal 2
streamlit run frontend/app.py
```

**Option B — Frontend only (self-contained, no backend needed)**
```bash
streamlit run frontend/app.py
```
> The frontend automatically falls back to direct service calls if the backend is unreachable.

---

## ⚙️ Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | — | Google Gemini API key from AI Studio |
| `GEMINI_MODEL` | No | `gemini-2.5-flash` | Gemini model variant |
| `BACKEND_URL` | No | `http://127.0.0.1:8000` | FastAPI backend URL |
| `WAQI_TOKEN` | No | `demo` | WAQI AQI API token (optional) |
| `REDIS_URL` | No | — | Redis URL for caching (optional) |
| `LOG_LEVEL` | No | `INFO` | Logging verbosity |

---

## 🌐 Deployment

### Streamlit Community Cloud (Recommended)

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your forked repository
4. Set `GEMINI_API_KEY` in Streamlit Secrets
5. Deploy — the app auto-installs dependencies and builds the SQLite database on first run

### Local Production

```bash
# Backend
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 2

# Frontend
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

---

## 📁 Project Structure

```
CivicMind-AI/
│
├── .github/
│   ├── workflows/
│   │   └── ci.yml              # GitHub Actions CI
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
│
├── backend/
│   ├── agents/                 # Domain AI agents
│   ├── data_sources/           # API + dataset loaders
│   ├── rag/                    # RAG pipeline (FAISS + embeddings)
│   ├── routers/                # FastAPI route handlers
│   ├── schemas/                # Pydantic validation models
│   ├── services/               # AI, weather, AQI services
│   └── main.py                 # FastAPI application entry
│
├── frontend/
│   ├── components/             # Reusable UI components
│   ├── pages/                  # Page modules (Dashboard, Analytics, etc.)
│   ├── styles/                 # CSS design system
│   ├── utils/                  # Dataset service helpers
│   └── app.py                  # Streamlit application entry
│
├── config/                     # City definitions and configuration
├── database/                   # SQLite manager and schema
├── datasets/                   # CSV source data + municipal guidelines
├── docs/                       # Project documentation
├── tests/                      # Pytest test suite
├── assets/                     # Visual assets (logo, screenshots)
│
├── .env.example                # Environment variable template
├── requirements.txt            # Python dependencies
├── CONTRIBUTING.md             # Contribution guide
├── CODE_OF_CONDUCT.md          # Community standards
├── SECURITY.md                 # Security policy
├── CHANGELOG.md                # Version history
└── README.md                   # This file
```

---

## 🗺 Roadmap

- [x] Multi-agent AI architecture
- [x] Real-time weather and AQI monitoring
- [x] GIS hospital and flood map layers
- [x] RAG decision engine with SOP retrieval
- [x] SQLite indexed data layer (32k+ records)
- [x] Premium UI with dark/light mode
- [x] Municipal report export (MD, CSV, JSON)
- [x] Self-contained Streamlit Cloud deployment
- [ ] WebSocket real-time sensor streaming
- [ ] IoT sensor integration
- [ ] Mobile application (Flutter)
- [ ] Satellite imagery layer (ISRO/Bhoonidhi)
- [ ] Predictive flood simulation engine
- [ ] Kubernetes deployment configuration
- [ ] User authentication and organization workspaces

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "feat: add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 🔒 Security

Found a vulnerability? See [SECURITY.md](SECURITY.md) for the responsible disclosure process.

---

## 📜 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 👤 Author

**P. Harshith Reddy**

[![GitHub](https://img.shields.io/badge/GitHub-Harshithreddy--ux-181717?style=flat-square&logo=github)](https://github.com/Harshithreddy-ux)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-P._Harshith_Reddy-0A66C2?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/p-harshith-reddy-679141333)

---

<div align="center">

⭐ **Star this repository** if CivicMind AI helped you or inspired your work!

*Made with ❤️ using AI, GIS, and Smart City Intelligence*

</div>
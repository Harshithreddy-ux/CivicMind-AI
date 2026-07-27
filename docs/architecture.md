# Architecture — CivicMind AI

## Overview

CivicMind AI is built as a **loosely coupled, layered architecture** with a clear separation between the presentation layer (Streamlit), the business logic layer (FastAPI + Agents), and the data layer (SQLite + External APIs).

The frontend can operate in two modes:

1. **Full-stack mode** — Streamlit calls FastAPI backend over HTTP
2. **Self-contained mode** — Streamlit imports backend services directly (for Streamlit Cloud deployment)

---

## System Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│                                                             │
│  Streamlit (frontend/app.py)                                │
│                                                             │
│  Pages: Home · Dashboard · Analytics · City Intelligence    │
│         Forecast · AI Assistant · Reports · Settings        │
│                                                             │
│  Components: Sidebar · Cards · Charts · Map · AI Panel      │
│              Risk Score · City Status · Footer              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      │  HTTP (full-stack) or Direct Import (cloud)
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   API / SERVICE LAYER                        │
│                                                             │
│  FastAPI (backend/main.py, port 8000)                       │
│                                                             │
│  Routers:                                                   │
│    /api/weather    → WeatherService (Open-Meteo HTTPX)      │
│    /api/aqi        → AQIService (WAQI HTTPX)                │
│    /api/analysis   → DecisionAgent (Gemini 2.5 Flash)       │
│    /api/hospitals  → HospitalAgent (SQLite query)           │
│    /health         → System health check                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  AGENT ORCHESTRATION LAYER                   │
│                                                             │
│  Supervisor → routes request to domain agents               │
│  Coordinator → manages parallel agent execution             │
│                                                             │
│  Domain Agents (backend/agents/):                           │
│    WeatherAgent   · AQIAgent     · FloodAgent               │
│    CrimeAgent     · HospitalAgent · DecisionAgent           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                     AI / RAG LAYER                           │
│                                                             │
│  google-genai SDK → Gemini 2.5 Flash                        │
│  FAISS vector store → municipal_guidelines.txt SOP index    │
│  text-embedding-004 → semantic similarity retrieval         │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      DATA LAYER                              │
│                                                             │
│  SQLite (database/civicmind.db)                             │
│    • hospital_directory  (32,000+ records, indexed)         │
│    • crime_dataset_india (20,000+ records)                  │
│    • metadata_indofloods (flood events)                     │
│    • subdivision_rainfall (IMD data)                        │
│    • catchment_characteristics                              │
│                                                             │
│  External APIs:                                             │
│    • Open-Meteo (weather, forecast) — no key required       │
│    • WAQI (AQI) — free demo token                           │
│    • OpenStreetMap / Nominatim (geocoding)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Design Decisions

### 1. Self-Contained Frontend Fallback
The frontend (`frontend/components/cards.py`) detects whether the FastAPI backend is reachable. If not, it imports and calls the backend services directly. This allows zero-config Streamlit Community Cloud deployment without a separate hosted backend.

### 2. SQLite over CSV
All large datasets are ingested once into an indexed SQLite database (`database/db_manager.py`) at application startup. This reduces per-query time from ~500ms (CSV parsing) to <5ms (SQL lookup).

### 3. Defensive Data Handling
All API responses are validated with `.get()` defaults before rendering. Missing keys, API failures, and empty datasets all result in graceful fallback UI — never a crash.

### 4. Async HTTP
All external API calls use `httpx.AsyncClient` within FastAPI async routes, preventing blocking on I/O.

---

## File Map

```
backend/
├── main.py                  FastAPI app, lifespan, routers
├── agents/
│   ├── supervisor.py        Routes requests to domain agents
│   ├── coordinator.py       Parallel agent execution
│   ├── decision_agent.py    Gemini synthesis + RAG retrieval
│   ├── flood_agent.py       Flood data analysis
│   ├── crime_agent.py       Crime pattern analysis
│   └── hospital_agent.py   Healthcare accessibility analysis
├── services/
│   ├── ai_service.py        Gemini client wrapper
│   ├── weather_service.py   Open-Meteo HTTPX client
│   └── aqi_service.py       WAQI HTTPX client
├── rag/
│   ├── document_loader.py   Indexes PDF/TXT/MD files via FAISS
│   └── retriever.py         Semantic similarity retrieval
├── data_sources/
│   ├── weather_api.py       Weather API data fetching
│   └── dataset_loader.py    SQLite → Pandas query helpers
└── schemas/
    ├── weather_schema.py    Pydantic weather models
    ├── aqi_schema.py        Pydantic AQI models
    └── decision_schema.py   Pydantic decision models

frontend/
├── app.py                   Streamlit entry point, routing
├── components/
│   ├── sidebar.py           Navigation, city selector, profile
│   ├── cards.py             Weather/AQI metric cards
│   ├── charts.py            Plotly time-series chart
│   ├── ai_panel.py          AI analysis display
│   ├── city_status.py       City operational status
│   ├── risk_score.py        Risk gauge component
│   ├── map_view.py          Folium GIS map layers
│   ├── branding.py          Logo and brand HTML
│   └── footer.py            Page footer
├── pages/
│   ├── home.py              Landing page
│   ├── dashboard.py         Main operational dashboard
│   ├── analytics.py         Historical charts
│   ├── forecast.py          7-day forecast
│   ├── city_map.py          GIS intelligence page
│   ├── assistant.py         AI chat interface
│   ├── reports.py           Export reports
│   └── settings.py          System settings
├── styles/
│   └── style.css            Design system (dark/light theme)
└── utils/
    └── dataset_service.py   Dataset query helpers for frontend
```

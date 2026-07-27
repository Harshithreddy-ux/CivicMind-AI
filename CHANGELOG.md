# Changelog

All notable changes to CivicMind AI are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project uses [Semantic Versioning](https://semver.org/).

---

## [1.1.0] — 2026-07-27

### Added
- **Home Landing Page** — animated hero section, real dataset metrics counters, interactive architecture flowchart, technology showcase grid, telemetry log terminal, and CTA navigation buttons
- **Sidebar User Profile** — operator avatar and role badge in sidebar footer
- **Settings Health Grid** — system connectivity badges for Gemini API, SQLite Engine, and Weather/AQI API
- **Light Mode Support** — CSS variables delegated to Streamlit theme tokens for full light/dark mode adaptability
- **`.env.example`** — documented environment variable template for new contributors
- **`CONTRIBUTING.md`** — contribution guide with branch naming and commit conventions
- **`SECURITY.md`** — responsible disclosure policy
- **`CODE_OF_CONDUCT.md`** — community standards (Contributor Covenant v2.1)
- **GitHub Actions CI** — automated linting, syntax checking, and test suite on every push and PR
- **Expanded test suite** — added tests for SQLite service layer, weather/AQI fallback logic, and dataset service functions

### Changed
- **Reports page** — replaced split HTML `cm-card` tags with native `st.container(border=True)` wrappers; download buttons converted to base64 anchor links
- **Charts component** — replaced split HTML card wrapper with native `st.container(border=True)`
- **CSS design system** — root colour variables linked to Streamlit theme properties; sidebar and hero backgrounds updated
- **Sidebar navigation** — "Home" added as first item; page selection persists to `session_state` enabling CTA redirects

### Fixed
- `KeyError: 'current'` crash in `risk_score.py` when weather API returns error payload
- `KeyError: 'State'` crash in `dataset_loader.py` due to SQLite column casing mismatch
- `SyntaxError: unterminated triple-quoted string` in `home.py` caused by successive broken patch attempts
- Deprecated `use_container_width=True` chart parameter replaced with `width='stretch'`

---

## [1.0.0] — 2026-07-26

### Added
- Initial production release
- Multi-agent AI architecture (Supervisor, Coordinator, Weather, AQI, Crime, Hospital, Flood, Decision agents)
- FastAPI async backend with HTTPX client
- SQLite indexed data layer (32,000+ hospital records, crime dataset, flood events)
- Streamlit frontend with dark mode premium UI
- Folium GIS maps with marker clustering, hospital layers, and flood overlays
- RAG pipeline with FAISS vector index over municipal SOP guidelines
- Google Gemini 2.5 Flash integration via official `google-genai` SDK
- 7-day weather and AQI forecast charts
- Pydantic v2 validation schemas
- Self-contained Streamlit Community Cloud deployment with backend fallback
- Structured Python logging throughout backend services

# Contributing to CivicMind AI

Thank you for your interest in contributing! We welcome improvements of all kinds — bug fixes, new features, documentation, and test coverage.

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/CivicMind-AI.git
   cd CivicMind-AI
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Copy and configure the environment:**
   ```bash
   cp .env.example .env
   # Add your GEMINI_API_KEY
   ```
5. **Run the app** to verify your setup:
   ```bash
   streamlit run frontend/app.py
   ```

---

## Branch Naming

| Type | Format | Example |
|---|---|---|
| Feature | `feature/<name>` | `feature/websocket-updates` |
| Bug fix | `fix/<name>` | `fix/risk-score-keyerror` |
| Documentation | `docs/<name>` | `docs/api-reference` |
| Refactor | `refactor/<name>` | `refactor/agent-coordinator` |
| Tests | `test/<name>` | `test/hospital-agent` |

---

## Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add WebSocket live sensor streaming
fix: handle missing "current" key in weather response
docs: add API setup guide to README
refactor: extract hospital query to dataset_service
test: add integration test for AQI agent
chore: update requirements.txt to Streamlit 1.35
```

---

## Pull Requests

- Open a PR against the `main` branch
- Describe what you changed and why
- Reference any related issues: `Closes #42`
- Ensure `pytest tests/ -v` passes before submitting
- Keep PRs focused — one change per PR

---

## Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use descriptive variable names
- Add docstrings to all public functions
- Use type hints for function signatures
- Keep functions under 50 lines where possible

---

## Reporting Bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- CivicMind AI version / commit hash
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behaviour
- Error traceback if available

---

## Suggesting Features

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md).

Before suggesting, check whether the feature is already in the [roadmap](README.md#roadmap).

---

## Questions?

Open a [GitHub Discussion](https://github.com/Harshithreddy-ux/CivicMind-AI/discussions) — we're happy to help.

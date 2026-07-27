# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| Latest (`main`) | ✅ Yes |
| Older branches | ❌ No |

---

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub Issues.**

If you discover a security vulnerability in CivicMind AI, please report it responsibly:

1. Email the maintainer at the address listed on the [GitHub profile](https://github.com/Harshithreddy-ux)
2. Include:
   - A description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (optional)

You will receive a response within **72 hours**.

We will acknowledge your report, investigate, and release a fix as quickly as possible. We ask that you **not disclose the vulnerability publicly** until a patch has been released.

---

## Security Practices in This Project

- **API keys** are loaded exclusively from environment variables — never hardcoded
- **SQL queries** use parameterised `pandas.read_sql_query` with bound parameters — no raw string interpolation
- **User inputs** from the Streamlit UI are validated before being passed to AI agents or SQL queries
- **Stack traces** are never surfaced to the end user — only graceful error messages are shown
- **Dependencies** are pinned to minimum secure versions in `requirements.txt`

---

## Known Limitations

- This project is primarily a **demonstration platform** — it is not hardened for multi-tenant production deployment without additional security review
- The optional Redis cache does not enforce authentication in development mode
- WebSocket endpoints (if added in future) should be protected with token authentication

from fastapi import FastAPI

app = FastAPI(
    title="CivicMind AI",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "status": "Backend Running",
        "project": "CivicMind AI"
    }
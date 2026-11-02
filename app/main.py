from fastapi import FastAPI

app = FastAPI(title="AI customer Support")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

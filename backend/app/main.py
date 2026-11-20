from fastapi import FastAPI

from .api import router

app = FastAPI(title="Es Magico Student Results Portal", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(router)

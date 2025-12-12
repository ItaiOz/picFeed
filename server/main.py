from fastapi import FastAPI
from fastapi.responses import Response
import csv
import io

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}
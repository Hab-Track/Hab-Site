import json
from fastapi import FastAPI

app = FastAPI(
    title="Hab Track - API",
    version="0.1"
)

with open("track_stats.json", "r") as f:
    data = json.load(f)


@app.get("/api/raw_data")
def get_raw_data():
    return data

@app.get("/api/another-route")
def fastapi_another_example():
    return {"message": "Another route in FastAPI"}
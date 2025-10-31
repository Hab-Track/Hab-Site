import json
from typing import Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Hab Track - API",
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
)

with open("datas/track_stats.json", "r") as f:
    data = json.load(f)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"]
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="docs")


@app.get("/raw_stats", tags=["General"], response_model=Dict[str, Dict[str, List[str]]], description="Returns all tracked statistics.")
def get_raw_stats():
    return data


@app.get("/latest_stats", tags=["General"], response_model=Dict[str, List[str]])
def get_latest_stats():
    latest_date = max(data.keys())
    return data[latest_date]


@app.get("/active_retros", tags=["General"], response_model=Dict[str, Dict[str, List[str]]], description="Returns all data for active retros.")
def get_active_retros():
    active_retros = set(data[max(data)].keys())
    filtered_data = {
        date: {retro: stats for retro, stats in retros.items() if retro in active_retros}
        for date, retros in data.items()
    }

    return filtered_data


@app.get("/date/{date}", tags=["By Date"], response_model=Dict[str, List[str]], description="Get statistics for a specific date. Use this format: YYYY-MM-DD")
def get_stats_by_date(date: str):
    if date not in data:
        raise HTTPException(status_code=404, detail="Date not found. Use this format: YYYY-MM-DD")
    
    return data[date]


@app.get("/retro/{retro}", tags=["By Retro"], response_model=Dict[str, List[str]], description="Get statistics for a specific retro.")
def get_stats_by_retro(retro: str):
    retro_data = {date: stats[retro] for date, stats in data.items() if retro in stats}
    if not retro_data:
        raise HTTPException(status_code=404, detail="Retro not found")

    return retro_data
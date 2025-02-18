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

with open("track_stats.json", "r") as f:
    data = json.load(f)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"]
)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="docs")


@app.get("/api/raw_stats", tags=["General"], response_model=Dict[str, Dict[str, List[str]]])
def get_raw_stats():
    """
    📊 Get all tracked statistics.

    - **Returns:** the entire dataset containing all retros and all dates.
    """
    return data


@app.get("/api/latest_stats", tags=["General"], response_model=Dict[str, List[str]])
def get_latest_stats():
    """
    🕒 Get the most recent statistics.

    - **Returns:** only the latest available data for all retros.
    """
    if not data:
        raise HTTPException(status_code=404, detail="No data available")
    
    latest_date = max(data.keys())
    return data[latest_date]


@app.get("/api/date/{date}", tags=["By Date"], response_model=Dict[str, List[str]])
def get_stats_by_date(date: str):
    """
    📅 Get statistics for a specific date.

    - **Format:** YYYY-MM-DD  
    - **Returns:** All retros with their data for the given date.
    """
    if date not in data:
        raise HTTPException(status_code=404, detail="Date not found. Use this format: YYYY-MM-DD")
    
    return data[date]


@app.get("/api/retro/{retro}", tags=["By Retro"], response_model=Dict[str, List[str]])
def get_stats_by_retro(retro: str):
    """
    🏨 Get statistics for a specific retro.

    - **Returns:** All dates where the given retro appears, along with its statistics.
    """
    retro_data = {date: stats[retro] for date, stats in data.items() if retro in stats}
    
    if not retro_data:
        raise HTTPException(status_code=404, detail="Retro not found")

    return retro_data
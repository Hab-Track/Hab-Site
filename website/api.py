from typing import Dict, List, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware

from .utils.fecth_data import fetch_data

app = FastAPI(
    title="Hab Track - API",
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
)

data = fetch_data("track_stats.json")
retro_info = fetch_data("retro_info.json")
retro_status = fetch_data("retro_status.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"]
)

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="docs")


### Stats

@app.get("/stats", tags=["Statistics"], response_model=Dict[str, Dict[str, List[str]]])
def get_raw_stats():
    return data

@app.get("/stats/last", tags=["Statistics"], response_model=Dict[str, List[str]])
def get_latest_stats():
    latest_date = max(data.keys())
    return data[latest_date]

@app.get("/stats/active_retros", tags=["Statistics"], response_model=Dict[str, Dict[str, List[str]]])
def get_active_retros():
    active_retros = set(data[max(data)].keys())
    filtered_data = {
        date: {retro: stats for retro, stats in retros.items() if retro in active_retros}
        for date, retros in data.items()
    }
    return filtered_data

@app.get("/stats/date/{date}", tags=["Statistics"])
def get_stats_by_date(date: str):
    if date not in data:
        raise HTTPException(status_code=404, detail="Date not found. Use format YYYY-MM-DD")
    return data[date]

@app.get("/stats/{retro}", tags=["Statistics"])
def get_stats_by_retro(retro: str):
    retro_data = {date: stats[retro] for date, stats in data.items() if retro in stats}
    if not retro_data:
        raise HTTPException(status_code=404, detail="Retro not found")
    return retro_data


### Info

@app.get("/retros/info", tags=["Retro Info"], response_model=Dict[str, Dict[str, Any]])
def get_all_retro_info():
    return retro_info

@app.get("/retros/info/{retro}", tags=["Retro Info"], response_model=Dict[str, Any])
def get_retro_info_by_name(retro: str):
    if retro not in retro_info:
        raise HTTPException(status_code=404, detail="Retro not found")
    return retro_info[retro]


### Status

@app.get("/retros/status", tags=["Retro Status"], response_model=Dict[str, Dict[str, Any]])
def get_all_retro_status():
    return retro_status

@app.get("/retros/status/{retro}", tags=["Retro Status"], response_model=Dict[str, Any])
def get_retro_status_by_name(retro: str):
    if retro not in retro_status:
        raise HTTPException(status_code=404, detail="Retro not found")
    return retro_status[retro]


### Utils

@app.get("/retros", tags=["Utility"], response_model=List[str])
def all_retros():
    return sorted(set(data[max(data)].keys()))

@app.get("/stats/dates", tags=["Utility"], response_model=List[str])
def all_dates():
    return sorted(data.keys())
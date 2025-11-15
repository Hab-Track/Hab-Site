import os
import time
import requests
from flask import jsonify
from dotenv import load_dotenv

load_dotenv()
API_BASE = os.environ.get("API_URL")

def check_api_availability():
    if not API_BASE:
        return False, "API URL is not configured."
    
    try:
        resp = requests.get(f"{API_BASE}/", timeout=5)
        return True, None
    except requests.RequestException as e:
        print(f"API is not accessible: {e}")
        return False, f"API is not accessible"

def process_search_query(search_query, selected_categories, selected_retros, search_in):
    if not search_query:
        return jsonify({'warning': 'No search query provided.'})
    
    if not search_in:
        return jsonify({'warning': 'Please select at least one search field.'})
    
    start_time = time.time()
    payload = {
        "search_query": search_query,
        "selected_categories": selected_categories,
        "selected_retros": selected_retros,
        "search_in": search_in
    }
    
    try:
        resp = requests.post(f"{API_BASE}/search/", json=payload)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return jsonify({"error": "Failed to fetch data from API."})
    
    execution_time = round(time.time() - start_time, 2)
    data['execution_time'] = execution_time
    
    if not data.get("results"):
        data['message'] = "No results found for your search."
    
    return jsonify(data)


def get_retros():
    try:
        resp = requests.get(f"{API_BASE}/retros/?debugtime", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        return data.get("retros", [])
    except requests.RequestException as e:
        print(f"Failed to fetch retros: {e}")
        return []


def get_retro_urls(selected_categories, selected_retros):
    payload = {
        "selected_categories": selected_categories,
        "selected_retros": selected_retros
    }
    try:
        resp = requests.post(f"{API_BASE}/retro-urls/", json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data
    except requests.RequestException as e:
        print(f"Failed to fetch retro URLs: {e}")
        return {}
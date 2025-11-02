import requests

GITHUB_REPO = "https://raw.githubusercontent.com/Hab-Track/stock/refs/heads/main/retros/"

def fetch_data(url):
    response = requests.get(GITHUB_REPO + url)
    response.raise_for_status()
    return response.json()
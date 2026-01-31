import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from website.api import app

client = TestClient(app)


class TestStatsEndpoints:
    def test_get_raw_stats(self):
        response = client.get("/stats")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_latest_stats(self):
        response = client.get("/stats/last")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_latest_retro_stats(self):
        response = client.get("/stats/retros/latest")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_active_retros(self):
        response = client.get("/stats/active_retros")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_stats_by_valid_date(self):
        response = client.get("/stats")
        dates = list(response.json().keys())
        
        if dates:
            valid_date = dates[0]
            response = client.get(f"/stats/date/{valid_date}")
            assert response.status_code == 200
            assert isinstance(response.json(), dict)

    def test_get_stats_by_invalid_date(self):
        response = client.get("/stats/date/2099-12-31")
        assert response.status_code == 404
        assert "Date not found" in response.json()["detail"]

    def test_get_stats_by_valid_retro(self):
        response = client.get("/retros")
        retros = response.json()
        
        if retros:
            valid_retro = retros[0]
            response = client.get(f"/stats/retro/{valid_retro}")
            assert response.status_code == 200
            assert isinstance(response.json(), dict)

    def test_get_stats_by_invalid_retro(self):
        response = client.get("/stats/retro/invalid_retro_xyz")
        assert response.status_code == 404
        assert "Retro not found" in response.json()["detail"]


class TestRetroInfoEndpoints:
    def test_get_all_retro_info(self):
        response = client.get("/retros/info")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_retro_info_by_valid_name(self):
        response = client.get("/retros/info")
        retros = list(response.json().keys())
        
        if retros:
            valid_retro = retros[0]
            response = client.get(f"/retros/info/{valid_retro}")
            assert response.status_code == 200
            assert isinstance(response.json(), dict)

    def test_get_retro_info_by_invalid_name(self):
        response = client.get("/retros/info/invalid_retro_xyz")
        assert response.status_code == 404
        assert "Retro not found" in response.json()["detail"]


class TestRetroStatusEndpoints:
    def test_get_all_retro_status(self):
        response = client.get("/retros/status")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_retro_status_by_valid_name(self):
        response = client.get("/retros/status")
        retros = list(response.json().keys())
        
        if retros:
            valid_retro = retros[0]
            response = client.get(f"/retros/status/{valid_retro}")
            assert response.status_code == 200
            assert isinstance(response.json(), dict)

    def test_get_retro_status_by_invalid_name(self):
        response = client.get("/retros/status/invalid_retro_xyz")
        assert response.status_code == 404
        assert "Retro not found" in response.json()["detail"]


class TestUtilityEndpoints:
    def test_get_all_retros(self):
        response = client.get("/retros")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data == sorted(data)

    def test_get_all_dates(self):
        response = client.get("/stats/dates")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert data == sorted(data)


class TestRootEndpoint:
    def test_root_redirect(self):
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "docs" in response.headers["location"]


class TestCORS:
    def test_cors_headers_options(self):
        response = client.options("/stats")
        if response.status_code == 200:
            assert "access-control-allow-origin" in response.headers or response.status_code == 200

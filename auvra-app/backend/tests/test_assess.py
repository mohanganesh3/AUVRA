import json
import sys, os
import httpx
from httpx import ASGITransport
import pytest
import pytest
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from app import app


@pytest.fixture
def anyio_backend():
    # Force asyncio backend to avoid missing trio dependency
    return "asyncio"

def valid_payload():
    return {
        "basic_info": {"name": "Mohan", "age": 20},
        "period_pattern": {"period_pattern": "regular", "birth_control": "hormonal_pills"},
        "cycle_details": {"last_period_date": "2025-10-17", "date_not_sure": False, "cycle_length": "21-25"},
        "health_concerns": {
            "period_concerns": ["irregular_periods"],
            "body_concerns": ["bloating"],
            "skin_hair_concerns": [],
            "mental_health_concerns": ["mood_swings"],
        },
        "top_concern": {"top_concern": "none"},
        "diagnosed_conditions": {"conditions": ["dysmenorrhea"], "others_input": "PCOS"},
        "lab_results": None,
    }

@pytest.mark.anyio
async def test_assess_valid_200():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/api/v1/assess", json=valid_payload())
        assert resp.status_code == 200, resp.text
        data = resp.json()
        assert "assessment_metadata" in data
        assert "primary_imbalance" in data


@pytest.mark.anyio
async def test_assess_invalid_cycle_length_422():
    transport = ASGITransport(app=app)
    bad = valid_payload()
    bad["cycle_details"]["cycle_length"] = "26_to_30"  # invalid literal
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/api/v1/assess", json=bad)
        assert resp.status_code == 422
        j = resp.json()
        assert j.get("detail")


@pytest.mark.anyio
async def test_assess_invalid_diagnosis_422():
    transport = ASGITransport(app=app)
    bad = valid_payload()
    bad["diagnosed_conditions"]["conditions"] = ["dysmenorrhea", "some_unknown"]
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/api/v1/assess", json=bad)
        assert resp.status_code == 422
        j = resp.json()
        assert j.get("detail")

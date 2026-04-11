"""
Job API Service - fetches real-time job postings.
Gracefully returns [] if API keys are not configured.
"""
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def fetch_jobs_jsearch(query: str, num_results: int = 10) -> list:
    api_key = getattr(settings, 'JSEARCH_API_KEY', '')
    if not api_key:
        return []
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    params = {"query": query, "page": "1", "num_pages": "1", "date_posted": "month"}
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return [
            f"{j.get('job_title', '')}\n{j.get('job_description', '')}"
            for j in data.get("data", [])[:num_results]
            if j.get("job_description")
        ]
    except Exception as e:
        logger.error(f"JSearch error: {e}")
        return []


def fetch_jobs_adzuna(query: str, num_results: int = 10) -> list:
    app_id = getattr(settings, 'ADZUNA_APP_ID', '')
    app_key = getattr(settings, 'ADZUNA_APP_KEY', '')
    if not app_id or not app_key:
        return []
    try:
        resp = requests.get(
            "https://api.adzuna.com/v1/api/jobs/in/search/1",
            params={"app_id": app_id, "app_key": app_key,
                    "results_per_page": num_results, "what": query},
            timeout=10
        )
        resp.raise_for_status()
        return [
            f"{j.get('title', '')}\n{j.get('description', '')}"
            for j in resp.json().get("results", [])[:num_results]
            if j.get("description")
        ]
    except Exception as e:
        logger.error(f"Adzuna error: {e}")
        return []


def fetch_job_descriptions(role_name: str) -> list:
    descriptions = fetch_jobs_jsearch(f"{role_name} jobs")
    if not descriptions:
        descriptions = fetch_jobs_adzuna(f"{role_name} jobs")
    return descriptions

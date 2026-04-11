"""
Role Matcher - scores candidate against all job roles.
"""
import json
import os
from typing import List, Dict
from .scoring_engine import calculate_match

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')


def load_job_roles() -> List[Dict]:
    path = os.path.join(DATA_DIR, 'job_roles.json')
    with open(path, 'r') as f:
        return json.load(f)


def match_all_roles(candidate_skills: List[str]) -> List[Dict]:
    roles = load_job_roles()
    results = []
    for role in roles:
        required_skills = role.get("required_skills", [])
        score_data = calculate_match(candidate_skills, required_skills)
        results.append({
            "role_id": role.get("id"),
            "title": role.get("title"),
            "category": role.get("category"),
            "description": role.get("description", ""),
            "icon": role.get("icon", "💼"),
            **score_data
        })
    results.sort(key=lambda x: x["match_percentage"], reverse=True)
    return results


def get_top_matches(candidate_skills: List[str], top_n: int = 6) -> List[Dict]:
    return match_all_roles(candidate_skills)[:top_n]


def generate_ai_suggestion(best_role: Dict) -> str:
    missing = best_role.get("missing_skills", [])
    role_title = best_role.get("title", "this role")
    match_pct = best_role.get("match_percentage", 0)

    if not missing:
        return (
            f"Excellent! You already have all the key skills for {role_title}. "
            f"Focus on building real-world projects to stand out."
        )
    if len(missing) <= 3:
        return (
            f"You're {match_pct}% there for {role_title}! "
            f"Learn {', '.join(missing)} to significantly boost your profile."
        )
    return (
        f"To land a {role_title} role (currently {match_pct}% match), prioritize: "
        f"{', '.join(missing[:4])}. These are the highest-demand skills."
    )

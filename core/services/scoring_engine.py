"""
Scoring Engine - calculates match percentage, matched/missing skills.
"""
from typing import List, Dict


def normalize_skills(skills: List[str]) -> List[str]:
    return [s.lower().strip() for s in skills if s]


def calculate_match(candidate_skills: List[str], required_skills: List[str]) -> Dict:
    candidate_set = set(normalize_skills(candidate_skills))
    required_set = set(normalize_skills(required_skills))

    matched = sorted(candidate_set & required_set)
    missing = sorted(required_set - candidate_set)
    bonus = sorted(candidate_set - required_set)

    pct = round((len(matched) / len(required_set)) * 100, 1) if required_set else 0.0

    return {
        "matched_skills": [s.capitalize() for s in matched],
        "missing_skills": [s.capitalize() for s in missing],
        "bonus_skills": [s.capitalize() for s in bonus],
        "match_percentage": pct,
        "total_required": len(required_set),
        "total_matched": len(matched),
        "total_missing": len(missing),
    }

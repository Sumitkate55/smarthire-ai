"""
Resume Analyzer - feedback, scoring, GitHub analysis.
"""
import re
import requests


def resume_feedback(raw_text: str, skills: list) -> list:
    feedback = []
    text_lower = raw_text.lower()
    word_count = len(raw_text.split())

    if word_count < 150:
        feedback.append({"type": "warning", "icon": "bi-exclamation-triangle",
                         "message": f"Resume is very short ({word_count} words). Aim for at least 300–500 words."})
    elif word_count < 300:
        feedback.append({"type": "info", "icon": "bi-info-circle",
                         "message": f"Resume could be more detailed ({word_count} words)."})
    else:
        feedback.append({"type": "success", "icon": "bi-check-circle",
                         "message": f"Good resume length ({word_count} words)."})

    section_checks = [
        (["project", "projects"], "Projects section missing. Add 2–3 relevant projects."),
        (["experience", "internship", "work experience"], "Work experience section not found."),
        (["education", "degree", "university", "college", "b.tech", "bca"], "Education section not detected."),
        (["skill", "skills", "technical skills"], "Skills section not clearly visible."),
    ]
    for keywords, msg in section_checks:
        if not any(kw in text_lower for kw in keywords):
            feedback.append({"type": "warning", "icon": "bi-exclamation-triangle", "message": msg})

    if not re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', raw_text):
        feedback.append({"type": "warning", "icon": "bi-envelope",
                         "message": "No email address found. Include contact info."})

    if len(skills) < 5:
        feedback.append({"type": "warning", "icon": "bi-tools",
                         "message": f"Only {len(skills)} skills detected. List more technical skills explicitly."})
    elif len(skills) >= 10:
        feedback.append({"type": "success", "icon": "bi-check-circle",
                         "message": f"Good skills coverage — {len(skills)} skills detected."})

    if not any(kw in text_lower for kw in ["github", "portfolio", "linkedin"]):
        feedback.append({"type": "info", "icon": "bi-link-45deg",
                         "message": "No GitHub, LinkedIn, or portfolio link found."})

    return feedback


def resume_score(raw_text: str, skills: list) -> dict:
    score = 0
    breakdown = []
    text_lower = raw_text.lower()
    word_count = len(raw_text.split())

    skill_pts = min(len(skills) * 2, 40)
    score += skill_pts
    breakdown.append({"label": "Skills Detected", "points": skill_pts, "max": 40,
                      "detail": f"{len(skills)} skills × 2 pts (max 40)"})

    length_pts = 30 if word_count >= 500 else 20 if word_count >= 300 else 10 if word_count >= 150 else 3
    score += length_pts
    breakdown.append({"label": "Resume Length", "points": length_pts, "max": 30,
                      "detail": f"{word_count} words"})

    section_pts = 0
    sections_found = []
    for kw_list, label in [
        (["experience", "internship", "work"], "Experience"),
        (["project", "projects"], "Projects"),
        (["education", "degree", "university", "college"], "Education"),
        (["@"], "Contact Email"),
    ]:
        if any(k in text_lower for k in kw_list):
            section_pts += 5
            sections_found.append(label)
    score += section_pts
    breakdown.append({"label": "Key Sections", "points": section_pts, "max": 20,
                      "detail": ", ".join(sections_found) if sections_found else "None found"})

    link_pts = 0
    if "github" in text_lower: link_pts += 4
    if "linkedin" in text_lower: link_pts += 4
    if any(k in text_lower for k in ["portfolio", "website", "behance"]): link_pts += 2
    link_pts = min(link_pts, 10)
    score += link_pts
    breakdown.append({"label": "Links & Profiles", "points": link_pts, "max": 10,
                      "detail": "GitHub, LinkedIn, Portfolio"})

    if score >= 80: grade, grade_type = "Excellent", "ok"
    elif score >= 60: grade, grade_type = "Good", "ok"
    elif score >= 40: grade, grade_type = "Fair", "warn"
    else: grade, grade_type = "Needs Work", "bad"

    return {"total": score, "max": 100, "grade": grade, "grade_type": grade_type, "breakdown": breakdown}


def github_analysis(username: str) -> dict:
    if not username or not username.strip():
        return {"error": "No username provided."}
    username = username.strip().lstrip("@")
    base = "https://api.github.com"
    headers = {"Accept": "application/vnd.github+json"}
    try:
        profile_resp = requests.get(f"{base}/users/{username}", headers=headers, timeout=8)
        if profile_resp.status_code == 404:
            return {"error": f"GitHub user '{username}' not found."}
        if profile_resp.status_code != 200:
            return {"error": "GitHub API unavailable. Try again later."}
        profile = profile_resp.json()

        repos_resp = requests.get(f"{base}/users/{username}/repos", headers=headers,
                                  params={"sort": "updated", "per_page": 30}, timeout=8)
        repos = repos_resp.json() if repos_resp.status_code == 200 else []

        lang_freq = {}
        top_repos = []
        for repo in repos:
            if isinstance(repo, dict) and not repo.get("fork"):
                lang = repo.get("language")
                if lang:
                    lang_freq[lang] = lang_freq.get(lang, 0) + 1
                top_repos.append({
                    "name": repo.get("name", ""),
                    "description": repo.get("description") or "",
                    "stars": repo.get("stargazers_count", 0),
                    "language": lang or "—",
                    "url": repo.get("html_url", ""),
                })
        top_repos.sort(key=lambda r: r["stars"], reverse=True)
        top_languages = sorted(lang_freq.items(), key=lambda x: x[1], reverse=True)

        return {
            "username": username,
            "name": profile.get("name") or username,
            "bio": profile.get("bio") or "",
            "avatar": profile.get("avatar_url", ""),
            "followers": profile.get("followers", 0),
            "following": profile.get("following", 0),
            "public_repos": profile.get("public_repos", 0),
            "profile_url": f"https://github.com/{username}",
            "top_repos": top_repos[:6],
            "top_languages": top_languages[:8],
            "error": None,
        }
    except requests.exceptions.Timeout:
        return {"error": "GitHub API timed out. Try again."}
    except Exception as e:
        return {"error": f"Could not fetch GitHub data: {e}"}

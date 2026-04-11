import uuid
import json
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from core.services.mongodb import resumes_col, scores_col
from core.services.role_matcher import get_top_matches, generate_ai_suggestion
from core.services.skill_extractor import SKILL_DICTIONARY
from core.services.resume_analyzer import resume_feedback, resume_score, github_analysis


@login_required
def analyze(request, resume_id):
    # FIXED: enforce ownership — user can only analyze their own resume
    resume = resumes_col().find_one(
        {"resume_id": resume_id, "user_id": request.user.id},
        {"_id": 0}
    )
    if not resume:
        raise Http404("Resume not found.")

    candidate_skills = resume.get("extracted_skills", [])
    candidate_set = set(s.lower() for s in candidate_skills)

    top_roles = get_top_matches(candidate_skills, top_n=6)
    if not top_roles:
        from django.contrib import messages
        messages.error(request, "Could not match any roles. Try uploading a more detailed resume.")
        return redirect('resumes:upload')

    best_role = top_roles[0]
    suggestion = generate_ai_suggestion(best_role)

    raw_text = resume.get("raw_text", "")
    r_feedback = resume_feedback(raw_text, candidate_skills)
    r_score = resume_score(raw_text, candidate_skills)

    github_data = None
    github_user = request.GET.get("github", "").strip()
    if github_user:
        try:
            github_data = github_analysis(github_user)
        except Exception:
            github_data = {"error": "GitHub fetch failed."}

    # Save score record (scoped to this user)
    score_doc = {
        "score_id": str(uuid.uuid4()),
        "user_id": request.user.id,
        "resume_id": resume_id,
        "best_role": best_role["title"],
        "match_percentage": best_role["match_percentage"],
        "matched_skills": best_role["matched_skills"],
        "missing_skills": best_role["missing_skills"],
        "top_roles": [
            {
                "title": r["title"],
                "match_percentage": r["match_percentage"],
                "icon": r.get("icon", "💼"),
                "category": r.get("category", ""),
            }
            for r in top_roles
        ],
        "ai_suggestion": suggestion,
        "resume_score": r_score["total"],
        "scored_at": datetime.utcnow().isoformat(),
    }
    scores_col().insert_one(score_doc)

    # Chart data
    top_role_labels = json.dumps([r["title"] for r in top_roles])
    top_role_scores = json.dumps([r["match_percentage"] for r in top_roles])

    cat_label_map = {
        "programming_languages": "Languages",
        "web_frontend": "Frontend",
        "web_backend": "Backend",
        "databases": "Databases",
        "cloud_devops": "Cloud/DevOps",
        "data_ai_ml": "AI/ML",
        "tools_version_control": "Tools",
        "mobile": "Mobile",
    }
    cat_labels, cat_counts = [], []
    for cat_key, skills_list in SKILL_DICTIONARY.items():
        matched_in_cat = [s for s in skills_list if s.lower() in candidate_set]
        if matched_in_cat:
            cat_labels.append(cat_label_map.get(cat_key, cat_key.replace("_", " ").title()))
            cat_counts.append(len(matched_in_cat))

    context = {
        "resume": resume,
        "best_role": best_role,
        "top_roles": top_roles,
        "suggestion": suggestion,
        "candidate_skills": [s.capitalize() for s in sorted(candidate_skills)],
        "top_roles_labels": top_role_labels,
        "top_roles_scores": top_role_scores,
        "skill_category_labels": json.dumps(cat_labels),
        "skill_category_counts": json.dumps(cat_counts),
        "r_feedback": r_feedback,
        "r_score": r_score,
        "github_data": github_data,
        "github_user": github_user,
    }
    return render(request, 'scoring/result.html', context)


@login_required
def score_history(request):
    # FIXED: always scoped to current user
    scores = list(scores_col().find(
        {"user_id": request.user.id},
        {"_id": 0}
    ).sort("scored_at", -1).limit(20))
    return render(request, 'scoring/history.html', {'scores': scores})

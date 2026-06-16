from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.services.mongodb import resumes_col, scores_col
from core.services.resume_analyzer import github_analysis


@login_required
def home(request):
    user_id = request.user.id

    resumes = list(resumes_col().find(
        {"user_id": user_id}, {"_id": 0, "raw_text": 0}
    ).sort("uploaded_at", -1).limit(5))

    scores = list(scores_col().find(
        {"user_id": user_id}, {"_id": 0}
    ).sort("scored_at", -1).limit(5))

    total_resumes = resumes_col().count_documents({"user_id": user_id})
    total_scores = scores_col().count_documents({"user_id": user_id})
    latest_score = scores[0] if scores else None
    avg_score = 0
    if scores:
        avg_score = round(sum(s.get("match_percentage", 0) for s in scores) / len(scores), 1)

    context = {
        "resumes": resumes,
        "scores": scores,
        "total_resumes": total_resumes,
        "total_scores": total_scores,
        "latest_score": latest_score,
        "avg_score": avg_score,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def github_lookup(request):
    github_user = request.GET.get('github', '').strip()
    github_data = None
    if github_user:
        try:
            github_data = github_analysis(github_user)
        except Exception:
            github_data = {"error": "GitHub profile fetch failed."}

    context = {
        "github_user": github_user,
        "github_data": github_data,
    }
    return render(request, 'dashboard/github_lookup.html', context)


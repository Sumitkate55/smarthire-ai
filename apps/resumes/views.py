import os
import uuid
from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from .forms import ResumeUploadForm
from core.services.mongodb import resumes_col
from core.services.resume_parser import parse_pdf
from core.services.skill_extractor import extract_skills


@login_required
def upload_resume(request):
    form = ResumeUploadForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        uploaded_file = request.FILES['resume']

        if not uploaded_file.name.lower().endswith('.pdf'):
            messages.error(request, "Only PDF files are accepted.")
            return render(request, 'resumes/upload.html', {'form': form})

        # Save file safely
        filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
        save_path = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

        with open(save_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Parse and extract
        try:
            text = parse_pdf(save_path)
            if not text.strip():
                messages.error(request, "Could not extract text from this PDF. Try a different file.")
                os.remove(save_path)
                return render(request, 'resumes/upload.html', {'form': form})
            skills = extract_skills(text)
        except Exception as e:
            messages.error(request, f"Could not parse resume: {e}")
            return render(request, 'resumes/upload.html', {'form': form})

        label = form.cleaned_data.get('name') or uploaded_file.name
        resume_id = str(uuid.uuid4())

        # Store in MongoDB — always tag with this user's ID
        doc = {
            "resume_id": resume_id,
            "user_id": request.user.id,          # CRITICAL: ownership tag
            "username": request.user.username,
            "label": label,
            "filename": filename,
            "raw_text": text,
            "extracted_skills": skills,
            "uploaded_at": datetime.utcnow().isoformat(),
        }
        resumes_col().insert_one(doc)

        messages.success(request, f"Resume parsed! Found {len(skills)} skills.")
        return redirect('scoring:analyze', resume_id=resume_id)

    return render(request, 'resumes/upload.html', {'form': form})


@login_required
def resume_history(request):
    # FIXED: always filter by current user's ID — no data leaks
    col = resumes_col()
    resumes = list(col.find(
        {"user_id": request.user.id},
        {"_id": 0, "raw_text": 0}        # exclude heavy raw_text field
    ).sort("uploaded_at", -1))
    return render(request, 'resumes/history.html', {'resumes': resumes})

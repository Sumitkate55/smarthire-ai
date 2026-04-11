from django.urls import path
from . import views

app_name = 'resumes'
urlpatterns = [
    path('upload/', views.upload_resume, name='upload'),
    path('history/', views.resume_history, name='history'),
]

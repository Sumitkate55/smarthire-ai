from django.urls import path
from . import views

app_name = 'scoring'
urlpatterns = [
    path('analyze/<str:resume_id>/', views.analyze, name='analyze'),
    path('history/', views.score_history, name='history'),
]

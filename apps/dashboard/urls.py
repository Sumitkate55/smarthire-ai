from django.urls import path
from . import views

app_name = 'dashboard'
urlpatterns = [
    path('', views.home, name='home'),
    path('github-lookup/', views.github_lookup, name='github_lookup'),
]

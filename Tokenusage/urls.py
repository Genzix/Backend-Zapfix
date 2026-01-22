from django.urls import path
from . import views

urlpatterns = [
    path('', views.tokens_create, name='tokens_create'),
    path('usage/', views.tokens_usage, name='tokens_usage'),
]
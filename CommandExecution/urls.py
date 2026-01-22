from django.urls import path
from . import views

urlpatterns = [
    path('', views.command_list_create, name='command_list_create'),  # GET: List, POST: Create
]


from django.urls import path
from . import views

urlpatterns = [
    path('', views.session_list_create, name='session_list_create'),  # GET: List, POST: Create
    path('<uuid:session_id>/', views.session_detail_update, name='session_detail_update'),  # GET: Detail, PATCH: Update
    path('<uuid:session_id>/messages/', views.session_add_message, name='session_add_message'),  # POST: Add message
]

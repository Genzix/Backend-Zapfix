from django.urls import path
from . import views

urlpatterns = [
    path('', views.message_list, name='message_list'),  # GET: List messages
    path('<uuid:message_id>/', views.message_detail, name='message_detail'),  # GET, PUT, PATCH, DELETE: Message operations
]


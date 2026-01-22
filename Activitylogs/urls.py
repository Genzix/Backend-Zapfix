from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.admin_users_list, name='admin_users_list'),
    path('activity/', views.admin_activity_summary, name='admin_activity_summary'),
    path('user/<int:user_id>/details/', views.admin_user_details, name='admin_user_details'),
]


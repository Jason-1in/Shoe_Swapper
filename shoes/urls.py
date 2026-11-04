"""Defines URL patterns for shoes."""
from django.urls import path
from . import views 

app_name = "shoes"

urlpatterns = [
    #Home page
    path('', views.index, name = "index"),
    path('my_shoes/', views.my_shoes, name='my_shoes'),
    path('new_shoe/', views.new_shoe, name='new_shoe'),
    path('edit_shoe/<int:shoe_id>/', views.edit_shoe, name='edit_shoe'),
    path('browse/', views.browse, name='browse'),
    path('shoe/<int:shoe_id>/', views.shoe_detail, name='shoe_detail'),
    path('shoe/<int:shoe_id>/request/', views.request_swap, name='request_swap'),
    path('requests/incoming/', views.incoming_requests, name='incoming_requests'),
    path('requests/mine/', views.my_requests, name='my_requests'),
    path('requests/<int:request_id>/respond/', views.respond_request, name='respond_request'),
    path('delete_shoe/<int:shoe_id>/', views.delete_shoe, name='delete_shoe')
]
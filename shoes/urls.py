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

]
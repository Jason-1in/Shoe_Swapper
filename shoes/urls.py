"""Defines URL patterns for shoes."""


from django.urls import path
from . import views 


app_name = "shoes"

urlpatterns = [
    #Home page
    path('', views.index, name = "index"),

]
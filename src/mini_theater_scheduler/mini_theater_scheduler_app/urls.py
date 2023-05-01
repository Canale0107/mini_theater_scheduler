from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    path('csv_view', views.csv_view, name='csv_view'),
]



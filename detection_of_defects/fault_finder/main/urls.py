from tkinter.font import names

from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.start_detection),
    path('start_detection', views.start_detection, name='start_detection'),
    path('result_detection', views.result_detection, name='upload'),
    path('report', views.do_report, name='report')
]
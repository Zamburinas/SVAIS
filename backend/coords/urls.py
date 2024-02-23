# myapp/urls.py
import coords.views as views
from django.urls import path


urlpatterns = [
    path('coords', views.coords, name='coords'),
]

# myapp/urls.py
import coords.views as views
from django.urls import path


urlpatterns = [
    path('coords', views.coords, name='coords'),
    path('get_route', views.get_route, name='get_route'),
    path('boat_info', views.boat_info, name='boat_info')
]

# myapp/urls.py
import coords.views as views
from django.urls import path


urlpatterns = [
    path('coords', views.coords, name='coords'),
    path('get_route', views.get_route, name='get_route'),
    path('boat_names', views.boat_names, name='boat_names'), 
    path('getProtectedAreas', views.getProtectedAreas, name='getProtectedAreas'),
    path('boatInfo', views.getBoatInfo, name='boatInfo'),
]

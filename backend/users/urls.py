# myapp/urls.py
import users.views as views
from django.urls import path


urlpatterns = [
    path('login', views.login, name='login'),
    path('checkToken', views.checkToken, name = 'checkToken'),
    path('register', views.register, name = 'register')
]

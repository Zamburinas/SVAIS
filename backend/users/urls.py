# myapp/urls.py
from django.urls import path
from users.views import login, checkToken

urlpatterns = [
    path('login', login, name='login'),
    path('checkToken', checkToken, name = 'checkToken')
]

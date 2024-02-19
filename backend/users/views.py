# myapp/views.py
import json
from users.utils import Authenticate
from django.http import JsonResponse, HttpResponse
from pymongo import MongoClient
from config import *

def login(request):
    if request.method == 'POST':
        # Assuming the frontend sends email and password in the request body
        body = json.loads(request.body)
        email = body.get('email', None)
        password = body.get('password', None)
        
        if email is None or password is None or not _check_credentials(email, password):
            return JsonResponse({'error': 'Email or password not valid'}, status = 400)
        
        token = Authenticate.encode_auth_token(email, minutes=60)
        return JsonResponse({"token": token})

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def auth_token(request):
    token = request.headers.get("Authorization")
    username = Authenticate.decode_auth_token(token)
    if Authenticate.decode_auth_token(token):
        return JsonResponse({"state": "OK", "username":username})
    else:
        return HttpResponse(status=401)

def _check_credentials(email, password):
    db = MongoClient(DATABASE_IP, DATABASE_PORT).get_database(DATABASE_NAME)
    user = db[Database.USERS.value].find_one({
        'email': email
    })
    if user and user['password'] == Authenticate.hash_password(password):
        return True

    return False

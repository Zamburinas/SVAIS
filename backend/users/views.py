# myapp/views.py
import json
import re
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

def register(request):
    if request.method == 'POST':
        # Assuming the frontend sends email and password in the request body
        body = json.loads(request.body)
        if any(i is None or len(i) == 0 for i in list(body.values())):
            return JsonResponse({'msg': 'Not valid data.'}, status = 400)
        
        if body['password'] != body['repeatPassword']:
            return JsonResponse({'msg': 'Password do not match.'}, status = 400)
        
        if not _is_valid_email(body['email']):
            return JsonResponse({'msg': 'Wrong email format.'}, status = 400)
        
        db = MongoClient(DATABASE_IP, DATABASE_PORT).get_database(DATABASE_NAME)
        user = db[Database.USERS.value].find_one({
            'email': body['email']
        })
        if user:
            return JsonResponse({'msg': 'User already exist.'}, status = 400)
        
        db[Database.USERS.value].insert_one({
            'email': body['email'],
            'password': Authenticate.hash_password(body['password']),
            'name': body['name'],
            'lastName': body['lastName'],
            'organization': body['organization']
        })

        return JsonResponse({"msg": 'User created succesfully.'})

    else:
        return JsonResponse({'msg': 'Method not allowed'}, status=405)
    
def checkToken(request):
    body = json.loads(request.body)
    token = body.get('token', None)
    username = Authenticate.decode_auth_token(token)

    if username:
        return JsonResponse({"state": "OK", "username":username})
    else:
        return HttpResponse(status=401)

def _is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

def _check_credentials(email, password):
    db = MongoClient(DATABASE_IP, DATABASE_PORT).get_database(DATABASE_NAME)
    user = db[Database.USERS.value].find_one({
        'email': email
    })
    if user and user['password'] == Authenticate.hash_password(password):
        return True

    return False

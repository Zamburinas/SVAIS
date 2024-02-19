# myapp/views.py
import json
from django.http import JsonResponse

def login(request):
    if request.method == 'POST':
        # Assuming the frontend sends email and password in the request body
        body = json.loads(request.body)
        email = body.get('email', None)
        password = body.get('password', None)
        return JsonResponse({'email': email, 'password': password})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


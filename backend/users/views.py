# myapp/views.py
import json
import re
import face_recognition
import base64
import numpy as np
import os
from users.utils import Authenticate
from django.http import JsonResponse, HttpResponse
from pymongo import MongoClient
from config import *
from io import BytesIO
from PIL import Image

collection = MongoClient(DATABASE_IP, DATABASE_PORT).get_database(DATABASE_NAME)[
    Database.USERS.value
]

desired_keys = ["email", "name", "organization", "two_factor_auth"]


def login(request):
    if request.method == "POST":
        # Assuming the frontend sends email and password in the request body
        body = json.loads(request.body)
        email = body.get("email", None)
        password = body.get("password", None)

        if email is None or password is None or not _check_credentials(email, password):
            return JsonResponse({"msg": "Email or password not valid"}, status=400)

        user_data = _get_credentials(email)
        if user_data["two_factor_auth"]:
            return JsonResponse(
                {"msg": "Two Factor Authentication required"}, status=400
            )

        token = Authenticate.encode_auth_token(email, minutes=60)
        return JsonResponse(
            {
                "token": token,
                "user_info": {key: user_data.get(key) for key in desired_keys},
            }
        )

    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def register(request):
    if request.method == "POST":
        # Assuming the frontend sends email and password in the request body
        body = json.loads(request.body)

        if any(i is None or len(i) == 0 for i in list(body.values())):
            return JsonResponse({"msg": "There's some missing field."}, status=400)

        if body["password"] != body["repeatPassword"]:
            return JsonResponse({"msg": "Password do not match."}, status=400)

        if not _is_valid_email(body["email"]):
            return JsonResponse({"msg": "Wrong email format."}, status=400)

        user = _get_credentials(body["email"])
        if user:
            return JsonResponse({"msg": "User already exist."}, status=400)

        collection.insert_one(
            {
                "email": body["email"],
                "password": Authenticate.hash_password(body["password"]),
                "name": body["name"],
                "lastName": body["lastName"],
                "organization": body["organization"],
                "two_factor_auth": False,
                "tfa_enc": None,
            }
        )

        return JsonResponse({"msg": "User created succesfully."})

    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def twoFactorAuth(request):
    if request.method == "POST":
        body = json.loads(request.body)

        base64_image = body["image"]
        email = body["email"]
        password = body["password"]

        if not _check_credentials(email, password):
            return JsonResponse({"msg": "Wrong credentials."}, status=400)
        if not base64_image:
            return JsonResponse({"msg": "Not valid image."}, status=400)

        try:
            collection.update_one(
                {"email": body["email"]},
                {
                    "$set": {
                        "two_factor_auth": True,
                        "tfa_enc": face_recognition.face_encodings(
                            _base64_to_numpy(base64_image)
                        )[0].tolist(),
                    }
                },
            )
        except Exception as e:
            with open("error.txt", "w") as file:
                file.write(str(e))
        return JsonResponse({"message": "Image uploaded successfully"})

    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def checkToken(request):
    body = json.loads(request.body)
    token = body.get("token", None)
    username = Authenticate.decode_auth_token(token)

    if username and _get_credentials(username):
        return JsonResponse({"state": "OK", "username": username})
    else:
        return HttpResponse(status=401)


def _is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def _get_credentials(email):
    return collection.find_one({"email": email})


def _check_credentials(email, password):
    user = _get_credentials(email)
    if user and user["password"] == Authenticate.hash_password(password):
        return True

    return False


def _two_factor_auth(user, face):
    user = _get_credentials(user)
    if not user:
        return False
    user_encoded = Authenticate.decrypt(["tfa_enc"])
    return face_recognition.compare_faces(
        [user_encoded], face_recognition.face_encodings(face)[0]
    )[0]


def _base64_to_numpy(base64_string):
    with open("image.jpg", "wb") as f:
        f.write(base64.b64decode(base64_string))

    known_image = face_recognition.load_image_file("image.jpg")

    os.remove("image.jpg")

    return known_image

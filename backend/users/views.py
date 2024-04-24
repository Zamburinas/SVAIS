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
        tfa = body.get("tfa", None)

        if email is None or password is None or not _check_credentials(email, password):
            return JsonResponse({"msg": "Credenciales no validas."}, status=400)

        user_data = get_credentials(email)
        if user_data["two_factor_auth"]:
            if tfa is None:
                return JsonResponse(
                    {"msg": "Se requiere de autenticacion en dos pasos.", "tfa": True},
                    status=400,
                )

            if not _two_factor_auth(email, tfa):
                return JsonResponse(
                    {"msg": "La autenticacion en dos pasos no coincide.", "tfa": True},
                    status=400,
                )

        token = Authenticate.encode_auth_token(email, minutes=60)
        return JsonResponse(
            {
                "token": token,
                "user_info": {key: user_data.get(key) for key in desired_keys},
                "msg": "Sesion iniciada correctamente.",
            }
        )

    else:
        return JsonResponse({"msg": "Method not allowed"}, status=405)


def register(request):
    if request.method == "POST":
        # Assuming the frontend sends email and password in the request body
        body = json.loads(request.body)

        if any(i is None or len(i) == 0 for i in list(body.values())):
            return JsonResponse({"msg": "Hay algun campo vacio."}, status=400)

        if body["password"] != body["repeatPassword"]:
            return JsonResponse({"msg": "Porfavor, revise sus credenciales."}, status=400)

        if not _is_valid_email(body["email"]):
            return JsonResponse({"msg": "Formato de correo incorrecto."}, status=400)

        user = get_credentials(body["email"])
        if user:
            return JsonResponse({"msg": "El usuario ya existe. Prueba a iniciar sesion."}, status=400)

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

        return JsonResponse({"msg": "Uusario creado correctamente."})

    else:
        return JsonResponse({"msg": "Metodo no permitido."}, status=405)


def twoFactorAuth(request):
    if request.method == "POST":
        body = json.loads(request.body)

        base64_image = body["image"]
        email = body["email"]
        password = body["password"]

        if not _check_credentials(email, password):
            return JsonResponse({"msg": "Credenciales erroneas."}, status=400)
        if not base64_image:
            return JsonResponse({"msg": "Imagen invalida."}, status=400)

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
            return JsonResponse({"msg": "Ha ocurrido un error."}, status=500)

        return JsonResponse({"message": "Autenticacion en dos pasos activada correctmanete."})

    else:
        return JsonResponse({"msg": "Metodo no permitido."}, status=405)


def disableTwoFactor(request):
    if request.method == "POST":
        body = json.loads(request.body)

        email = body["email"]
        password = body["password"]

        if not _check_credentials(email, password):
            return JsonResponse({"msg": "Credenciales erroneas."}, status=400)

        try:
            collection.update_one(
                {"email": body["email"]},
                {
                    "$set": {
                        "two_factor_auth": False,
                        "tfa_enc": None,
                    }
                },
            )
        except Exception as e:
            return JsonResponse({"msg": "Ha ocurrido un error."}, status=500)

        return JsonResponse(
            {"message": "Autenticacion en dos pasos deshabilitada correctamente."}
        )

    else:
        return JsonResponse({"msg": "Metodo no permitido."}, status=405)


def checkToken(request):
    body = json.loads(request.body)
    token = body.get("token", None)
    username = Authenticate.decode_auth_token(token)

    if username and get_credentials(username):
        return JsonResponse({"state": "OK", "username": username})
    else:
        return HttpResponse(status=401)


def _is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


def get_credentials(email):
    return collection.find_one({"email": email})


def _check_credentials(email, password):
    user = get_credentials(email)
    if user and user["password"] == Authenticate.hash_password(password):
        return True

    return False


def _two_factor_auth(user, face):
    user = get_credentials(user)
    if not user:
        return False
    user_encoded = user["tfa_enc"]
    face = _base64_to_numpy(face)
    try:
        face_encodings = face_recognition.face_encodings(face)[0]
    except:
        return False

    return face_recognition.compare_faces([np.array(user_encoded)], face_encodings)[0]


def _base64_to_numpy(base64_string):
    with open("image.jpg", "wb") as f:
        f.write(base64.b64decode(base64_string))

    try:
        known_image = face_recognition.load_image_file("image.jpg")
    except:
        known_image = np.array([])

    os.remove("image.jpg")

    return known_image

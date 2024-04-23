import json
import pytz
import subprocess
import os
import wave
import pandas as pd
from django.http import JsonResponse, HttpResponse
from pymongo import MongoClient
from config import *
from scipy.stats import chi2
from datetime import datetime, timedelta
from pyais import decode
from datetime import datetime
from users.views import get_credentials
from pyais.exceptions import MissingMultipartMessageException
import re


# Create your views here.
radiogonos = [
    (42.254605, -8.865245),
    (42.111481, -8.898115),
    (42.198248, -8.906154),
]
db = MongoClient(DATABASE_IP, DATABASE_PORT).get_database(DATABASE_NAME)
madrid_timezone = pytz.timezone("Europe/Madrid")

def lastHour(request):
    if request.method == "GET":
        # Calculate the time for one hour ago
        one_hour_ago = datetime.now(madrid_timezone) - timedelta(hours=5)

        pipeline = [
            {
                "$match": {
                    "BaseDateTime": {"$gte": one_hour_ago.strftime("%d-%m-%YT%H:%M:%S")}
                }  # Match documents within the last hour
            },
            {
                "$sort": {
                    "BaseDateTime": -1
                }  # Sort by BaseDateTime in descending order
            },
            {
                "$group": {
                    "_id": "$MMSI",
                    "MMSI": {"$first": "$MMSI"},
                    "LAT": {"$first": "$LAT"},
                    "LON": {"$first": "$LON"},
                }
            },
        ]
        resultados = list(db[Database.COORDS.value].aggregate(pipeline))
        resultados_filtered = []
        for item in resultados:
            if not any(value is None for value in item.values()):
                item["_id"] = str(item["_id"])
                resultados_filtered.append(item)

        return JsonResponse({"boats": resultados_filtered, "radiogonos": radiogonos})
    else:
        return JsonResponse({"error": "Metodo no permitido"}, status=405)

def coords(request):
    if request.method == "GET":
        pipeline = [
            {
                "$sort": {
                    "BaseDateTime": -1
                }  # Ordenar por BaseDateTime en orden descendente
            },
            {
                "$group": {
                    "_id": "$MMSI",
                    "MMSI": {"$first": "$MMSI"},
                    "LAT": {"$first": "$LAT"},
                    "LON": {"$first": "$LON"},
                }
            },
        ]

        resultados = list(db[Database.COORDS.value].aggregate((pipeline)))
        resultados_filtered = []
        for item in resultados:
            if not any(value is None for value in item.values()):
                item["_id"] = str(item["_id"])
                resultados_filtered.append(item)


        return JsonResponse({"boats": resultados_filtered, "radiogonos": radiogonos})

    elif request.method == "POST":
        data = json.loads(request.body)
        email = data.get("email")
        if not email:
            return JsonResponse({"msg": "Please provide a valid email."}, status=400)

        credentials = get_credentials(email=email)
        if not credentials:
            return JsonResponse({"msg": "Please provide a valid email."}, status=400)
        nmea_sentence = data.get("nmea", None)
        if nmea_sentence is None:
            return JsonResponse({"msg": "Wrong message format"}, status=400)
        try:
            nmea_sentence = [nmea.encode("utf-8") for nmea in nmea_sentence.split("\n")]
            decoded_message = decode(*nmea_sentence).asdict()
            decoded_message = _convert_enum_to_string(decoded_message)
            current_datetime = datetime.now(madrid_timezone)

            formatted_date = current_datetime.strftime(
                "%d-%m-%Y"
            )  # Day-month-year format
            formatted_time = current_datetime.strftime(
                "%H:%M:%S"
            )  # Hour:minute:second format

            time_received = {
                "day": formatted_date,
                "hour": formatted_time,
                "BaseDateTime": f"{formatted_date}T{formatted_time}",
            }
            if decoded_message.get("SHIPNAME", None) is None:
                time_received["SHIPNAME"] = get_boat_name(decoded_message.get("MMSI"))

            decoded_message.update(time_received)
            db[Database.COORDS.value].insert_one(decoded_message)

        except Exception as e:
            return JsonResponse({"msg": "Wrong message format"}, status=400)

        return JsonResponse({"msg": "Coord received succesfully."})
    else:
        return JsonResponse({"error": "Metodo no permitido"}, status=405)


def get_route(request):
    if request.method == "POST":
        body = json.loads(request.body)
        min_distance = 0.0005
        pipeline = [
            {"$match": {"MMSI": body["MMSI"]}},
            {"$sort": {"BaseDateTime": 1}},
            {"$project": {"_id": 0, "LAT": 1, "LON": 1, "BaseDateTime": 1, "SPEED": 1}},
        ]

        resultado = list(db[Database.COORDS.value].aggregate(pipeline))
        resultado_filtered = []
        for i in resultado:
            if i.get("LAT", None) is not None:
                resultado_filtered.append(i)

        filtered_result = filtrar_coordenadas(resultado_filtered, min_distance)

        final_routes = detect_new_routes(filtered_result)

        response_data = []

        for route in final_routes:
            route_data = [
                (
                    doc.get("LAT", None),
                    doc.get("LON", None),
                    doc.get("BaseDateTime", None),
                    doc.get("SPEED", None),
                )
                for doc in route
            ]
            response_data.append({"route": route_data})

        return JsonResponse(response_data, safe=False)
    else:
        return JsonResponse({"error": "Metodo no permitido"}, status=405)


def detect_new_routes(resultado):
    routes = []
    current_route = []

    for i in range(len(resultado)):
        tiempo_actual = datetime.strptime(
            resultado[i]["BaseDateTime"], "%d-%m-%YT%H:%M:%S"
        )

        if i > 0:
            tiempo_anterior = datetime.strptime(
                resultado[i - 1]["BaseDateTime"], "%d-%m-%YT%H:%M:%S"
            )
            tiempo_diff = tiempo_actual - tiempo_anterior
        else:
            tiempo_diff = timedelta(minutes=0)

        if tiempo_diff > timedelta(minutes=60):
            if current_route:
                routes.append(current_route)
                current_route = [
                    current_route[-1]
                ]  # Comenzar la nueva ruta con el último punto de la ruta anterior

        current_route.append(resultado[i])

    if current_route:
        routes.append(current_route)

    return routes


def filtrar_coordenadas(resultado, min_distance=0.0005):
    if min_distance == 0 or len(resultado) < 2:
        # Si la distancia mínima es cero o solo hay un punto, devolver solo la última posición
        if resultado:
            return [resultado[-1]]
        return []

    filtered_result = []
    movimiento_iniciado = False
    puntos_en_movimiento = []

    for i in range(1, len(resultado)):
        lat_diff = abs(resultado[i]["LAT"] - resultado[i - 1]["LAT"])
        lon_diff = abs(resultado[i]["LON"] - resultado[i - 1]["LON"])

        if lat_diff > min_distance or lon_diff > min_distance:
            if movimiento_iniciado:
                puntos_en_movimiento.append(resultado[i])
            else:
                # Guardar el primer punto de cuando estuvo parado
                primer_punto_parado = resultado[i - 1]
                movimiento_iniciado = True
                puntos_en_movimiento.append(
                    resultado[i - 1]
                )  # Agregar el último punto parado
                puntos_en_movimiento.append(
                    resultado[i]
                )  # Agregar el primer punto en movimiento
        else:
            if movimiento_iniciado:
                # Guardar el último punto que estuvo parado
                ultimo_punto_parado = resultado[i - 1]
                movimiento_iniciado = False
                filtered_result.append(primer_punto_parado)
                filtered_result.extend(puntos_en_movimiento)
                filtered_result.append(ultimo_punto_parado)
                puntos_en_movimiento = []  # Reiniciar lista de puntos en movimiento

    # Si la trayectoria termina con movimiento, agregar el último punto
    if movimiento_iniciado:
        filtered_result.append(primer_punto_parado)
        filtered_result.extend(puntos_en_movimiento)
        filtered_result.append(resultado[-1])

    # Si no hay cambios significativos en la posición del vehículo, agregar la última posición
    if not filtered_result:
        filtered_result.append(resultado[-1])

    return filtered_result


def boat_names(request):
    if request.method == "GET":

        # Aquí consultar base de datos para que devuelva información de los datos, como el nombre y el MMSI

        pipeline = [
            {
                "$match": {"SHIPNAME": {"$ne": "Desconocido"}}
            },  # Filter out documents where SHIPNAME is "Desconocido"
            {
                "$group": {"_id": "$MMSI", "SHIPNAME": {"$first": "$SHIPNAME"}}
            },  # Group by MMSI and select first non-"Desconocido" SHIPNAME
            {
                "$project": {"_id": 0, "MMSI": "$_id", "SHIPNAME": 1}
            },  # Project the fields
        ]

        resultados = list(db[Database.COORDS.value].aggregate(pipeline))
        return JsonResponse(json.dumps(resultados), safe=False)
    if request.method == "POST":

        body = json.loads(request.body)

        clave = next(iter(body))
        valor = body[clave]
        if clave != "SHIPNAME":
            try:
                # Define the regex pattern to match the MMSI values containing the specified integer string
                regex_pattern = rf".*{valor}.*$"
                # Query the collection using the regex pattern
                resultados = db[Database.COORDS.value].find(
                    {
                        "$expr": {
                            "$regexMatch": {
                                "input": {"$toString": f"${clave}"},
                                "regex": regex_pattern,
                                "options": "i",  # Optional: case-insensitive
                            }
                        }
                    }
                )
            except:
                resultados = []
        else:
            regex = re.compile(re.escape(valor), re.IGNORECASE)
            resultados = db[Database.COORDS.value].find({clave: {"$regex": regex}})

        vessel_names_set = set()

        for resultado in resultados:

            vessel_names_set.add(resultado["SHIPNAME"])

        vessel_names_unique = list(vessel_names_set)
        return JsonResponse(json.dumps(vessel_names_unique), safe=False)
    else:
        return JsonResponse({"error": "Metodo no permitido"}, status=405)


def get_boat_name(mmsi):
    boat_info = db[Database.COORDS.value].find({"MMSI": mmsi})
    names = {
        boat["SHIPNAME"]
        for boat in boat_info
        if boat.get("SHIPNAME", "desconocido").lower() != "desconocido"
    }
    if names:
        return names.pop()
    return "Desconocido"


def get_boat_type(mmsi):
    boat_info = db[Database.COORDS.value].find({"MMSI": mmsi})
    types = {
        boat["SHIP_TYPE"]
        for boat in boat_info
        if boat.get("SHIP_TYPE", "desconocido") != "desconocido"
    }
    if types:
        boat_type = types.pop()
        VesselType_aux = db[Database.VESSELTYPE.value].find_one(
            {"vesselType": {"$regex": str(boat_type)}}
        )
        return VesselType_aux["description"]
    return "Desconocido"


def getBoatInfo(request):
    if request.method == "POST":
        body = json.loads(request.body)

        pipeline = [
            {"$match": {"MMSI": body}},  # Filtrar por el MMSI concreto
            {
                "$sort": {
                    "BaseDateTime": -1
                }  # Ordenar por BaseDateTime en orden descendente
            },
            {
                "$group": {
                    "_id": "$MMSI",
                    "data": {
                        "$first": "$$ROOT"
                    },  # Tomar el primer documento después de ordenar
                }
            },
        ]
        resultados = list(db[Database.COORDS.value].aggregate(pipeline))
        if not resultados:
            return JsonResponse({"error": "Boat not found"}, status=400)

        resultados = resultados[0]

        resultados["data"]["SHIP_TYPE"] = get_boat_type(resultados["data"]["MMSI"])
        resultados["data"]["SHIPNAME"] = get_boat_name(resultados["data"]["MMSI"])
        try:
            Status_aux = db[Database.STATUS.value].find_one(
                {"status": resultados["data"]["STATUS"]}
            )
            resultados["data"]["STATUS"] = Status_aux["description"]
        except:
            resultados["data"]["STATUS"] = "Desconocido"

        del resultados["_id"]
        del resultados["data"]["_id"]

        return JsonResponse(resultados, safe=False)
    else:
        return JsonResponse({"error": "Metodo no permitido"}, status=405)


def getProtectedAreas(request):
    if request.method == "GET":

        areas = list(
            db[Database.AREAS.value].find()
        )  # Convertir el resultado a una lista de documentos

        # Eliminar el campo '_id' de cada documento
        for area in areas:
            del area["_id"]

        return JsonResponse(areas, safe=False)

    else:
        return JsonResponse({"error": "Metodo no permitido"}, status=405)


def _convert_enum_to_string(data: dict):
    converted_data = {}
    for key, value in data.items():
        if isinstance(value, Enum):
            value = value.value
        elif isinstance(value, bytes):
            value = int.from_bytes(value)
        converted_data[key.upper()] = value
    return converted_data


def decode_file(request):
    if request.method == "POST":
        try:
            # Get the uploaded file from the request
            uploaded_file = request.FILES["file"]
        except KeyError:
            return JsonResponse({"msg": "No file uploaded."}, status=400)

        # Check the file size
        if uploaded_file.size > 100 * 1024 * 1024:  # 100 MB
            return JsonResponse(
                {"msg": "File exceeds maximum limit of 100 MB."}, status=400
            )

        # Save the file to a temporary location
        file_path = os.path.join("/tmp", uploaded_file.name)
        with open(file_path, "wb") as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        # Determine the file type
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        if file_extension != ".raw":
            file_path_raw = file_path.replace(file_extension, ".raw")
            try:
                wav_to_raw(file_path, file_path_raw)
            except:
                return JsonResponse(
                    {"msg": "Ha ocurrido un error al decodificar el mensaje."},
                    status=400,
                )
            file_path = file_path_raw

        # Set the paths and parameters for the decoding command
        ais_path = "~/LPRO/aisdecoder/build/"
        command = (
            f"{ais_path}aisdecoder -h 127.0.0.1 -p 12345 -a file -f {file_path} -d"
        )

        # Execute the decoding command
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        output = result.stderr.split("\n")
        decoded_messages = _decode_messages(output)

        # Remove the temporary file
        os.remove(file_path)
        if not decoded_messages:
            return JsonResponse(
                {"msg": "El archivo no tiene ningun mensajes"}, status=400
            )
        # Return the decoded result as JSON response
        return JsonResponse(
            {
                "msg": "Archivo decodificado correctamente.",
                "json": decoded_messages,
                "routes": _new_routes_json(decoded_messages),
                "menu": _get_menu_data(decoded_messages),
            },
            safe=False,
        )
    else:
        return JsonResponse({"msg": "Metodo no permitido"}, status=405)


def wav_to_raw(input_wav_file, output_raw_file):
    # Open the WAV file for reading
    with wave.open(input_wav_file, "rb") as wav_file:
        # Read audio data
        audio_data = wav_file.readframes(wav_file.getnframes())

    # Write the audio data to a raw file
    with open(output_raw_file, "wb") as raw_file:
        raw_file.write(audio_data)


def convert_wav_to_raw(input_wav_file, output_raw_file):
    # Execute the sox command to convert the WAV file to a raw file
    subprocess.run(["sox", input_wav_file, output_raw_file])


def _get_menu_data(messages):
    # Assuming messages is a dictionary containing the JSON data
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(messages)

    # Apply the aggregation pipeline steps using pandas operations
    # Step 1: Filter out documents where SHIPNAME is "Desconocido"
    # df_filtered = df[df['SHIPNAME'] != 'Desconocido']

    # Step 2: Group by MMSI and select first non-"Desconocido" SHIPNAME
    df_grouped = df.groupby("MMSI").first().reset_index()

    # Step 3: Project the fields
    # df_projected = df_grouped.loc[:, ['MMSI', 'SHIPNAME']]

    # Convert the DataFrame to a JSON object
    result_json = df_grouped.to_json(orient="records")

    # Return the JSON object
    return json.loads(result_json)


def _decode_messages(messages):
    nmea_sentence = []
    decoded_messages = []
    for message in messages:
        nmea_sentence.append(message.encode("utf-8"))
        try:
            decoded_message = decode(*nmea_sentence).asdict()
            decoded_message = _convert_enum_to_string(decoded_message)
            decoded_message["BaseDateTime"] = datetime.now(madrid_timezone).strftime(
                "%d-%m-%YT%H:%M:%S"
            )
            decoded_messages.append(decoded_message)
            nmea_sentence = []
        except MissingMultipartMessageException as missing:
            continue
        except Exception as e:
            nmea_sentence = []
    return decoded_messages


def _add_names(resultado):
    names = {
        i["MMSI"]: i["SHIPNAME"]
        for i in resultado
        if i.get("SHIPNAME", None) is not None
    }
    resultado_new = []
    for i in resultado:
        if i["MMSI"] in names:
            i["SHIPNAME"] = names[i["MMSI"]]
        else:
            i["SHIPNAME"] = "Desconocido"
        resultado_new.append(i)
    return resultado_new


def _group_mmsi(data):
    grouped = {}
    for i in data:
        mmsi = i["MMSI"]
        if mmsi in grouped:
            grouped[mmsi].append(i)
        else:
            grouped[mmsi] = [i]
    return grouped


def _new_routes_json(resultado):
    resultado = _add_names(resultado)
    resultado_filtered = []
    for i in resultado:
        if i.get("LAT", None) is not None:
            resultado_filtered.append(i)

    grouped_data = _group_mmsi(resultado_filtered)

    response_data = {}
    for key, value in grouped_data.items():
        response_data_inter = []
        filtered_result = filtrar_coordenadas(value)

        final_routes = detect_new_routes(filtered_result)

        for route in final_routes:
            route_data = [
                (
                    doc.get("LAT", None),
                    doc.get("LON", None),
                    doc.get("BaseDateTime", None),
                    doc.get("SPEED", None),
                )
                for doc in route
            ]
            response_data_inter.append({"route": route_data})
        response_data[key] = response_data_inter
    return response_data

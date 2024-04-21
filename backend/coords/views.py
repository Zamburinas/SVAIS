import json
import pytz
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from pymongo import MongoClient
from config import *
from scipy.stats import chi2
from datetime import datetime, timedelta
from pyais.messages import AISSentence
from datetime import datetime
from users.views import get_credentials

# Create your views here.

db = MongoClient(DATABASE_IP, DATABASE_PORT).get_database(DATABASE_NAME)
madrid_timezone = pytz.timezone('Europe/Madrid')

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

        radiogonos = [
            (43.6728903, -7.8391903),
            (56.130366, -106.346771),
            (-34.61315, -58.37723),
        ]
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
            decoded_message = (
                AISSentence(nmea_sentence.encode("utf-8")).decode().asdict()
            )
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
            if decoded_message.get('SHIPNAME', None) is None:
                time_received['SHIPNAME'] = get_boat_name(decoded_message.get('MMSI'))

            decoded_message.update(time_received)
            db[Database.COORDS.value].insert_one(decoded_message)

        except:
            return JsonResponse({"msg": "Wrong message format"}, status=400)

        return JsonResponse({"msg": "Coord received succesfully."})
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


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
        return JsonResponse({"error": "Method not allowed"}, status=405)


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


def filtrar_coordenadas(resultado, min_distance):
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
            {"$group": {"_id": "$MMSI", "SHIPNAME": {"$first": "$SHIPNAME"}}},
            {"$project": {"_id": 0, "MMSI": "$_id", "SHIPNAME": 1}},
        ]

        resultados = list(db[Database.COORDS.value].aggregate(pipeline))
        return JsonResponse(json.dumps(resultados), safe=False)
    if request.method == "POST":

        body = json.loads(request.body)

        query = body
        pipeline = [
            {
                "$match": query  # Utiliza la consulta proporcionada para filtrar los resultados
            },
            {"$group": {"_id": "$SHIPNAME"}},
            {
                "$project": {
                    "_id": 0,  # Excluye el campo "_id"
                    "SHIPNAME": "$_id",  # Renombra "_id" a "VesselName"
                }
            },
        ]
        resultados = db[Database.COORDS.value].aggregate(pipeline)
        vessel_names_set = set()
        for resultado in resultados:
            vessel_names_set.add(resultado["SHIPNAME"])

        vessel_names_unique = list(vessel_names_set)
        return JsonResponse(json.dumps(vessel_names_unique), safe=False)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


def get_boat_name(mmsi):
    boat_info = db[Database.COORDS.value].find({"MMSI": mmsi, "MSG_TYPE": 5})
    unique_name = {boat["SHIPNAME"] for boat in boat_info if boat["SHIPNAME"].lower() != 'desconocido'}
    if unique_name:
        return unique_name[0]
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

        resultados["data"]["VesselType"] = "Desconocido"
        resultados["data"]["VesselName"] = "Desconocido"

        try:
            Status_aux = db[Database.STATUS.value].find_one(
                {"status": resultados["data"]["STATUS"]}
            )
            resultados["data"]["STATUS"] = Status_aux["description"]
        except:
            resultados["data"]["STATUS"] = "Desconocido"

        boat_info = db[Database.COORDS.value].find_one(
            {"MMSI": resultados["data"]["MMSI"], "MSG_TYPE": 5}
        )
        if boat_info:
            VesselType_aux = db[Database.VESSELTYPE.value].find_one(
                {"vesselType": {"$regex": str(boat_info["SHIP_TYPE"])}}
            )
            resultados["data"]["VesselType"] = VesselType_aux["description"]
            resultados["data"]["VesselName"] = boat_info["SHIPNAME"]

        del resultados["_id"]
        del resultados["data"]["_id"]

        return JsonResponse(resultados, safe=False)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


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
        return JsonResponse({"error": "Method not allowed"}, status=405)


def _convert_enum_to_string(data: dict):
    converted_data = {}
    for key, value in data.items():
        if isinstance(value, Enum):
            value = value.value
        elif isinstance(value, bytes):
            value = int.from_bytes(value)
        converted_data[key.upper()] = value
    return converted_data

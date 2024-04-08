from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from pymongo import MongoClient
from config import *
from scipy.stats import chi2
import json
from datetime import datetime
import math
# Create your views here.



def coords(request):
    if request.method == 'GET':
        db = MongoClient(DATABASE_IP, DATABASE_PORT).get_database(DATABASE_NAME)
        pipeline = [
            {
                '$sort': {'BaseDateTime': -1}  # Ordenar por BaseDateTime en orden descendente
            },
            {
                '$group': {
                    '_id': '$MMSI',
                    'data': {'$first': '$$ROOT'}  # Tomar el primer documento después de ordenar
                }
            }
        ]

        resultados = list(db[Database.COORDS.value].aggregate((pipeline)))
        
        for item in resultados:
            item['_id'] = str(item['_id'])
            item['data']['_id'] = str(item['data']['_id'])

        radiogonos=[
            (43.6728903,-7.8391903) ,
            (56.130366,-106.346771) ,
            (-34.61315,-58.37723) 
        ]

        return JsonResponse({"boats": json.dumps(resultados), "radiogonos": radiogonos})

    elif request.method == 'POST':
        #En funcion del barco seleccionado devuelve los datos de la elipse 
        print("as")
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_route(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        min_distance = 0.001
        db = MongoClient(DATABASE_IP, DATABASE_PORT).get_database(DATABASE_NAME)

        pipeline = [
            {
                "$match": {
                    "MMSI": body['MMSI']
                }
            },
            {
                "$sort": {
                    "BaseDateTime": 1
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "LAT": 1,
                    "LON": 1,
                    "BaseDateTime": 1,
                    "SOG": 1
                }
            }
        ]
        
        resultado = list(db[Database.COORDS.value].aggregate(pipeline))

        filtered_result=filtrar_coordenadas(resultado, min_distance)
        
        return JsonResponse({"route": [(doc["LAT"], doc["LON"],doc["BaseDateTime"],doc["SOG"]) for doc in filtered_result]})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)




def filtrar_coordenadas(resultado, min_distance):
    if min_distance == 0 or len(resultado) < 2:
        # Si la distancia mínima es cero o solo hay un punto, devolver solo la última posición
        return [resultado[-1]]

    filtered_result = []
    movimiento_iniciado = False
    puntos_en_movimiento = []

    for i in range(1, len(resultado)):
        lat_diff = abs(resultado[i]["LAT"] - resultado[i-1]["LAT"])
        lon_diff = abs(resultado[i]["LON"] - resultado[i-1]["LON"])

        if lat_diff > min_distance or lon_diff > min_distance:
            if movimiento_iniciado:
                puntos_en_movimiento.append(resultado[i])
            else:
                # Guardar el primer punto de cuando estuvo parado
                primer_punto_parado = resultado[i-1]
                movimiento_iniciado = True
                puntos_en_movimiento.append(resultado[i-1])  # Agregar el último punto parado
                puntos_en_movimiento.append(resultado[i])  # Agregar el primer punto en movimiento
        else:
            if movimiento_iniciado:
                # Guardar el último punto que estuvo parado
                ultimo_punto_parado = resultado[i-1]
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

    print(len(filtered_result))
    return filtered_result



def boat_info(request):
    if request.method == 'GET':
        
        #Aquí consultar base de datos para que devuelva información de los datos, como el nombre y el MMSI
        db = MongoClient(DATABASE_IP, DATABASE_PORT).get_database(DATABASE_NAME)

        pipeline = [
            {
                "$group": {
                    "_id": "$MMSI",
                    "VesselName": {"$first": "$VesselName"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "MMSI": "$_id",
                    "VesselName": 1
                }
            }
        ]

        resultados = list(db[Database.COORDS.value].aggregate(pipeline))

        return JsonResponse(json.dumps(resultados), safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)








def getProtectedAreas(request):
    if request.method == 'GET':
        db = MongoClient(DATABASE_IP, DATABASE_PORT).get_database(DATABASE_NAME)
        areas = list(db[Database.AREAS.value].find())  # Convertir el resultado a una lista de documentos
        
        # Eliminar el campo '_id' de cada documento
        for area in areas:
            del area['_id']
        
        return JsonResponse(areas, safe=False) 
        
    else: 
        return JsonResponse({'error': 'Method not allowed'}, status=405)
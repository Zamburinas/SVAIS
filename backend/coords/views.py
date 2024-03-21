from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from pymongo import MongoClient
from config import *
import numpy as np
from scipy.stats import chi2
import json
import random
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
        
        #Consultar base de datos para que te devuelva todos los objetos con el mismo MMSI
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
                    "LON": 1
                }
            }
        ]

        resultado = list(db[Database.COORDS.value].aggregate(pipeline))
        
        return JsonResponse({"route": [(doc["LAT"], doc["LON"]) for doc in resultado]})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


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





def generate_route(start_lat,start_lon,end_lat,end_lon,num_points):

    # Inicializamos la lista de coordenadas
    route = []

    # Generamos los puntos intermedios
    for i in range(num_points):
        # Interpolamos las coordenadas entre el inicio y la llegada
        lat = start_lat + (end_lat - start_lat) * (i / num_points)
        lon = start_lon + (end_lon - start_lon) * (i / num_points)

        # Añadimos un ligero desplazamiento aleatorio para simular el movimiento del barco
        lat += random.uniform(-0.005, 0.005)
        lon += random.uniform(-0.005, 0.005)

        route.append([lat, lon])

    return {'route': route}


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
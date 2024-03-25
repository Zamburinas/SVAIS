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
        min_distance = 0.0001
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
        filtered_result = [resultado[0]]
        for i in range(1, len(resultado)):
            lat_diff = abs(resultado[i]["LAT"] - filtered_result[-1]["LAT"])
            lon_diff = abs(resultado[i]["LON"] - filtered_result[-1]["LON"])
            if lat_diff > min_distance or lon_diff > min_distance:
                filtered_result.append(resultado[i])
                
        for i in range(1, len(resultado)):
            # Convertir las cadenas de fecha y hora en objetos datetime
            datetime1 = datetime.strptime(resultado[i - 1]["BaseDateTime"], "%Y-%m-%dT%H:%M:%S")
            datetime2 = datetime.strptime(resultado[i]["BaseDateTime"], "%Y-%m-%dT%H:%M:%S")
            
            # Calcular la diferencia de tiempo entre los puntos
            time_diff = (datetime2 - datetime1).total_seconds() / 3600  # Convertir a horas
            
            # Calcular la velocidad utilizando la distancia y el tiempo
            # (aquí puedes usar la fórmula de distancia entre dos puntos en la superficie de la Tierra)
            lat1 = math.radians(resultado[i - 1]["LAT"])
            lon1 = math.radians(resultado[i - 1]["LON"])
            lat2 = math.radians(resultado[i]["LAT"])
            lon2 = math.radians(resultado[i]["LON"])
            
            # Calcular la distancia utilizando la función corregida
            distance = calculate_distance(lat1, lon1, lat2, lon2)
            speed = distance / time_diff if time_diff != 0 else 0
            
            # Comparar la velocidad calculada con la velocidad proporcionada en el campo SOG
            sog = resultado[i]["SOG"]
            print(f"Velocidad calculada: {speed} nudos, SOG: {sog} nudos")
            if(speed>200):
                print(resultado[i])
        
        return JsonResponse({"route": [(doc["LAT"], doc["LON"]) for doc in filtered_result]})
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)



def calculate_distance(lat1, lon1, lat2, lon2):
    # Convertir grados decimales a radianes
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Radio de la Tierra en kilómetros
    R = 6371.0
    
    # Diferencia de latitud y longitud
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    # Fórmula de Haversine
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    # Distancia entre los dos puntos
    distance = R * c
    
    return distance


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
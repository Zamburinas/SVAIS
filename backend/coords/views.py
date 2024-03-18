from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from pymongo import MongoClient
from config import *
import numpy as np
from scipy.stats import chi2
import json
# Create your views here.


def coords(request):
    if request.method == 'GET':
        #devolver de la base de datos las ultimas coordenadas de los barcos y antenas
        boats = [
            (42.242306, -8.730914),
            (42.249000, -8.731020)
        ]
        radiogonos=[
            (43.6728903,-7.8391903) ,
            (56.130366,-106.346771) ,
            (-34.61315,-58.37723) 
        ]

        
        def calcular_elipse_error(coordinates):
        # Calcular la media de las coordenadas
            mean_x = np.mean(coordinates[:, 0])
            mean_y = np.mean(coordinates[:, 1])

            # Calcular la matriz de covarianza
            covariance_matrix = np.cov(coordinates, rowvar=False)

            # Calcular los autovalores y autovectores de la matriz de covarianza
            eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)

            # Calcular los ángulos de los autovectores
            angle = np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])

            # Calcular el factor de escala usando la distribución Chi-cuadrado
            confidence_level = 0.95
            chi_square_value = chi2.ppf(confidence_level, 2)
            scale_factor = np.sqrt(chi_square_value)

            # Calcular los semiejes de la elipse
            semi_major_axis = scale_factor * np.sqrt(eigenvalues[0])
            semi_minor_axis = scale_factor * np.sqrt(eigenvalues[1])

            return mean_x, mean_y, semi_major_axis, semi_minor_axis, np.degrees(angle)
        
        elipses = []
    # Calcular elipse de error para cada barco
        for index,boat in enumerate(boats):
            nearby_radiogonos = radiogonos  # Puedes filtrar aquí los radiogonos cercanos según tus criterios
            nearby_radiogonos = np.array(nearby_radiogonos)
            mean_x, mean_y, semi_major_axis, semi_minor_axis, angle = calcular_elipse_error(nearby_radiogonos)



                                        # Esto de aquí es basicamente ahora el centro de la elipse está puesto para que sea el centro del barco
            
            if index==1:
                boat_data = [boat[0], boat[1], boat[0], boat[1], semi_major_axis, semi_minor_axis, angle]
            else: 
                boat_data = [boat[0], boat[1], boat[0]+0.02, boat[1], semi_major_axis, semi_minor_axis, angle]

            elipses.append(boat_data)

        return JsonResponse({"boats": elipses, "radiogonos": radiogonos})

    elif request.method == 'POST':
        #En funcion del barco seleccionado devuelve los datos de la elipse 
        print("as")
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def get_route(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        print(body['name'])
        boats = [
            {   'route': [
                [42.242306, -8.730914],
                [42.243306, -8.731914],
                [42.244306, -8.732914],
                [42.245306, -8.733914],
                [42.246306, -8.734914],
                [42.247306, -8.735914],
                [42.248306, -8.736914],
                [42.249306, -8.737914],
                [42.250306, -8.738914],
                [42.251306, -8.739914]
            ] },
            {  'route': [
                [42.249000, -8.731020],
                [42.248000, -8.732020],
                [42.247000, -8.733020],
                [42.246000, -8.734020],
                [42.245000, -8.735020],
                [42.244000, -8.736020],
                [42.243000, -8.737020],
                [42.242000, -8.738020],
                [42.241000, -8.739020],
                [42.240000, -8.740020]
            ] },
            {   'route': [
                [42.240000, -8.741020],
                [42.241000, -8.742020],
                [42.242000, -8.743020],
                [42.243000, -8.744020],
                [42.244000, -8.745020],
                [42.245000, -8.746020],
                [42.246000, -8.747020],
                [42.247000, -8.748020],
                [42.248000, -8.749020],
                [42.249000, -8.750020]
            ] }
        # Agrega más elementos según sea necesario
        ]

        if body['name'] == "Barco 1":
            return JsonResponse(boats[0], safe=False)
        elif body['name'] == "Barco 2":
            return JsonResponse(boats[1], safe=False)
        elif body['name'] == "Barco 3":
            return JsonResponse(boats[2], safe=False)
        else:
            return JsonResponse({'error': 'Barco no encontrado'}, status=404)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def boat_info(request):
    if request.method == 'GET':

        #En un futuro devolverá el tipo de embarcación y se mandará y será el frontend quien decida la foto

        boats = [
            { 'name': 'Barco 2','photo': 'src/assets/cruise_colored-icon.png' },
            { 'name': 'Barco 3','photo': 'src/assets/cruise_colored-icon.png' },
            { 'name': 'Barco 4','photo': 'src/assets/cruise_colored-icon.png' }
        ]
        return JsonResponse(boats, safe=False)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)
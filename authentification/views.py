from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.db import connection

import json
from api.utils import *



class UtilisateurCreationView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))

            username = data.get('username')
            password = data.get('password')
            email = data.get('email')

            with connection.cursor() as cursor:
                cursor.execute("INSERT INTO utilisateur (username, password, email) VALUES (%s, %s, %s)",
                               [username, make_password(password), email])

                utilisateur_id = cursor.lastrowid

            token = generate_jwt_token(utilisateur_id, username)

            response_data = {
                'message': 'Utilisateur créé avec succès',
                'token': token
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            error_response = {
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        



class UtilisateurConnexionView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body.decode('utf-8'))

            username = data.get('username')
            password = data.get('password')

            with connection.cursor() as cursor:
                cursor.execute("SELECT id, password FROM utilisateur WHERE username = %s", [username])
                result = cursor.fetchone()

                if result and check_password(password, result[1]):
                    utilisateur_id = result[0]

                    token = generate_jwt_token(utilisateur_id, username)

                    response_data = {
                        'message': 'Connexion réussie',
                        'token': token
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    error_response = {
                        'error': 'Nom d\'utilisateur ou mot de passe incorrect'
                    }
                    return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            error_response = {
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

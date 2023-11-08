from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection

from api.utils import *
from .facade import *

import openai
import os
import environ 
import requests
import json

env = environ.Env()
environ.Env.read_env()
config = Config('/api/.env')

openai.api_key = os.getenv("OPENAI_API_KEY")

clipdrop_api_key= os.getenv("SD_API_KEY")

class PersonnageCreationView(APIView):
    def post(self, request, univers_id):
        name = json.loads(request.body.decode('utf-8')).get('name')
        response = PersonnageFacade.create_personnage(request, univers_id, name)
        return response



class PersonnageListeView(APIView):
    def get(self, request, univers_id):
        try:

            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])

            if utilisateur_id is not None:

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, name, description, imagePathUrl FROM personnage WHERE id_univers = %s", [univers_id])
                    result = cursor.fetchall()

                personnages = []
                for row in result:
                    personnage_info = {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'imagePathUrl': row[3]
                    }
                    personnages.append(personnage_info)

                return Response({'personnages': personnages}, status=status.HTTP_200_OK)

            else:
                error_response = {
                    'error': 'Token invalide'
                }
                return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        except (DecodeError, ExpiredSignatureError) as e:
            error_response = {
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            error_response = {
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)
        
class PersonnageModifView(APIView):
    def put(self, request, univers_id, personnage_id):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])

            if utilisateur_id is not None:

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM personnage WHERE id = %s AND id_univers = %s", [personnage_id, univers_id])
                    result = cursor.fetchone()

                if result:
                    data = request.data  
                    name = data.get('name')
                    description = data.get('description')
                    imagePathUrl = data.get('imagePathUrl')

                    with connection.cursor() as cursor:
                        cursor.execute("UPDATE personnage SET name = %s, description = %s, imagePathUrl = %s WHERE id = %s", [name, description, imagePathUrl, personnage_id])

                    response_data = {
                        'message': 'Personnage modifié avec succès'
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Personnage non trouvé dans l\'univers'}, status=status.HTTP_404_NOT_FOUND)

            else:
                error_response = {
                    'error': 'Token invalide'
                }
                return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        except (DecodeError, ExpiredSignatureError) as e:
            error_response = {
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            error_response = {
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)


class PersonnageSuppView(APIView):
    def delete(self, request, univers_id, personnage_id):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id FROM personnage WHERE id = %s AND id_univers = %s", [personnage_id, univers_id])
                    result = cursor.fetchone()

                if result:
                    with connection.cursor() as cursor:
                        cursor.execute("DELETE FROM personnage WHERE id = %s", [personnage_id])

                    response_data = {
                        'message': 'Personnage supprimé avec succès'
                    }
                    return Response(response_data, status=status.HTTP_204_NO_CONTENT)
                else:
                    return Response({'error': 'Personnage non trouvé dans l\'univers'}, status=status.HTTP_404_NOT_FOUND)

            else:
                error_response = {
                    'error': 'Token invalide'
                }
                return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        except (DecodeError, ExpiredSignatureError) as e:
            error_response = {
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            error_response = {
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection

from api.utils import *
from .facade import *

import openai
import os
import json 
import environ 
import requests


env = environ.Env()
environ.Env.read_env()
config = Config('/api/.env')

openai.api_key = os.getenv("OPENAI_API_KEY")

clipdrop_api_key= os.getenv("SD_API_KEY")

# Votre code de vue avec l'utilisation de UniversFacade.
class UniversCreationView(APIView):

    # Fait appel à la vue creation_univers de la l'univers facade
    def post(self, request):
        name = json.loads(request.body.decode('utf-8')).get('name')
        response = UniversFacade.create_univers(request, name)
        return response
 
 
 # Vue qui gére l'affichage des univers.
class UniversListeView(APIView):

    # Vue get qui gére l'affichage en liste des univers.
    def get(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
            utilisateur_id = validate_jwt_token(token)
            if utilisateur_id is not None:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, name, description, imagePathUrl, id_utilisateur FROM univers")
                    result = cursor.fetchall()

                univers_list = []
                for row in result:
                    univers_info = {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'imagePathUrl': row[3],
                        'id_utilisateur': row[4]
                    }
                    univers_list.append(univers_info)

                return Response({'univers': univers_list}, status=status.HTTP_200_OK)
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


 # Vue qui gére l'affichage en détails des univers.
class UniversDetailView(APIView):

    # Vue get qui affiche en détail d'un univers
    def get(self, request, univers_id):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, name, description, imagePathUrl, id_utilisateur FROM univers WHERE id = %s", [univers_id])
                    result = cursor.fetchone()

                if result:
                    univers_info = {
                        'id': result[0],
                        'name': result[1],
                        'description': result[2],
                        'imagePathUrl': result[3],
                        'id_utilisateur': result[4]
                    }
                    return Response({'univers': univers_info}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Univers non trouvé'}, status=status.HTTP_404_NOT_FOUND)

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
        

# Vue qui gère la modification d'un univers
class UniversModifView(APIView):

    # Vue put permet de modifier un univers
    def put(self, request, univers_id):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                data = request.data
                name = data.get('name')

                with connection.cursor() as cursor:
                    cursor.execute("SELECT name FROM univers WHERE id = %s", [univers_id])
                    result = cursor.fetchone()
                    if result and result[0] != name:
                        cursor.execute("UPDATE univers SET name = %s WHERE id = %s AND id_utilisateur = %s",
                                       [name, univers_id, utilisateur_id])

                        new_description = UniversFacade.generate_univers_description(name)

                        new_summary = UniversFacade.generate_summary(name, new_description)
                        new_image_path = UniversFacade.generate_and_save_image(name, new_summary)

                        cursor.execute("UPDATE univers SET description = %s, imagePathUrl = %s WHERE id = %s AND id_utilisateur = %s",
                                       [new_description, new_image_path, univers_id, utilisateur_id])

                        UniversFacade.image_generation_success(new_image_path)

                    else:
                        pass

                if cursor.rowcount > 0:
                    return Response({'message': 'Univers modifié avec succès'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': "L'univers n'a pas été trouvé ou vous n'avez pas la permission de le modifier"}, status=status.HTTP_404_NOT_FOUND)

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


        
# Vue qui supprime un utilisateur
class UniversSuppView(APIView):
    #Vue qui permet de supprimer un univers
    def delete(self, request, univers_id):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
               
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM univers WHERE id = %s AND id_utilisateur = %s",
                                   [univers_id, utilisateur_id])

                print("DELETE FROM univers WHERE id = %s AND id_utilisateur = %s" % (univers_id, utilisateur_id))

                if cursor.rowcount > 0:
                    return Response({'message': 'Univers supprimé avec succès'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': "L'univers n'a pas été trouvé ou vous n'avez pas la permission de le supprimer"}, status=status.HTTP_404_NOT_FOUND)

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
  
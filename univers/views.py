from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection

from api.utils import *


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

class UniversCreationView(APIView):
    def post(self, request):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])

            if utilisateur_id is not None:
                # Récupérez le nom de l'univers et la description à partir des données de la requête
                data = json.loads(request.body.decode('utf-8'))
                name = data.get('name')

                description = generate_univers_description(name)

                # Utilisez ChatGPT pour générer un résumé de la description
                summary = generate_summary(name, description)

                # Créez un prompt pour générer une image
                prompt = f"Generate an image of the univers {name} with the following summary: {summary}"

                # Appelez l'API Text-to-Image pour générer l'image
                r = requests.post('https://clipdrop-api.co/text-to-image/v1',
                                  files={
                                      'prompt': (None, prompt, 'text/plain')
                                  },
                                  headers={'x-api-key': clipdrop_api_key}
                )

                if r.ok:
                    # Le reste de votre code pour enregistrer l'image, enregistrer le chemin, etc.
                    image_data = r.content

                    # Enregistrez l'image sur le serveur avec un nom unique
                    image_path = f"media/img/univers/{name}.png"  # Utilisez un nom unique basé sur le nom de l'univers
                    with open(image_path, 'wb') as image_file:
                        image_file.write(image_data)

                    # Enregistrez le chemin de l'image dans le champ imagePathUrl
                    imagePathUrl = image_path

                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO univers (name, description, imagePathUrl, id_utilisateur) VALUES (%s, %s, %s, %s)",
                                       [name, description, imagePathUrl, utilisateur_id])

                    # Répondez avec un message de succès et le résumé généré
                    response_data = {
                        'message': 'Univers créé avec succès',
                        'description': description,
                        'summary': summary,
                        'imagePathUrl': imagePathUrl
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    # Gestion des erreurs en cas d'échec de l'appel à ClipDrop
                    error_response = {
                        'error': f'Erreur lors de la génération de l\'image: {r.status_code} - {r.text}'
                    }
                    return Response(error_response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                error_response = {
                    'error': 'Token invalide'
                }
                return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            error_response = {
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)

def generate_univers_description(name):
    # Utilisez ChatGPT pour générer la description
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in creating descriptions for fictional universe."},
            {"role": "user", "content": f"Generate a description for the universe {name},  less 500 characters."}
        ]
    )

    # Récupérez la réponse générée par ChatGPT
    description = response.choices[0].message['content']

    return description


def generate_summary(name, description):
    # Utilisez ChatGPT pour générer un résumé

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert with extensive knowledge about the {name} universe"},
            {"role": "user", "content": f"Generate a summary of the description {description} to create a Text-to-Image prompt for the {name} universe in under 200 characters."}
        ],
    )
    
    # Récupérez la réponse générée par ChatGPT
    summary = response.choices[0].message['content']  # Assignez la valeur de summary à la réponse générée par ChatGPT

    return summary





class UniversListeView(APIView):
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

class UniversDetailView(APIView):
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
        

class UniversModifView(APIView):
    def put(self, request, univers_id):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                data = request.data
                name = data.get('name')
                description = data.get('description')
                imagePathUrl = data.get('imagePathUrl')

                with connection.cursor() as cursor:
                    cursor.execute("UPDATE univers SET name = %s, description = %s, imagePathUrl = %s WHERE id = %s AND id_utilisateur = %s",
                                   [name, description, imagePathUrl, univers_id, utilisateur_id])

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
        

class UniversSuppView(APIView):
    def delete(self, request, univers_id):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
               
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM univers WHERE id = %s AND id_utilisateur = %s",
                                   [univers_id, utilisateur_id])

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
  
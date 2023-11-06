from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection

from api.utils import *

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
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])

            if utilisateur_id is not None:
                data = json.loads(request.body.decode('utf-8'))
                name = data.get('name')

                # Utilisez ChatGPT pour générer une description du personnage
                description = generate_character_description(name)

                # Utilisez ChatGPT pour générer un résumé de la description
                summary = generate_summary(name, description)

                # Utilisez ClipDrop pour générer l'image du personnage avec le prompt
                prompt = f"shot of {name} character with the following summary: {summary}"
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
                    image_path = f"media/img/personnages/{name}.png"  # Utilisez un nom unique basé sur le nom du personnage
                    with open(image_path, 'wb') as image_file:
                        image_file.write(image_data)

                    imagePathUrl = image_path

                    with connection.cursor() as cursor:
                        cursor.execute("INSERT INTO personnage (name, description, imagePathUrl, id_univers) VALUES (%s, %s, %s, %s)",
                                       [name, description, imagePathUrl, univers_id])

                    # Répondez avec un message de succès et les informations du personnage créé
                    response_data = {
                        'message': 'Personnage créé avec succès',
                        'description': description,
                        'summary': summary,
                        'imagePathUrl': imagePathUrl
                    }
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
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

def generate_character_description(character_name):
    # Utilisez ChatGPT pour générer la description
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an expert in creating character descriptions."},
            {"role": "user", "content": f"Generate a description for the character {character_name}"}
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
            {"role": "system", "content": "You are an expert in generating character descriptions and summaries."},
            {"role": "user", "content": f"Generate a summary of the description {description} to create a Text-to-Image prompt for the {name} universe in under 200 characters."}
        ]
    )
    
    # Récupérez la réponse générée par ChatGPT
    summary = response.choices[0].message['content']

    return summary



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
                        'id': row['id'],
                        'name': row['name'],
                        'description': row['description'],
                        'imagePathUrl': row['imagePathUrl']
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
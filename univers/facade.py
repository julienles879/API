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

class UniversFacade:
    @staticmethod
    def create_univers(request, name):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])

            if utilisateur_id is not None:
                description = UniversFacade.generate_univers_description(name)
                summary = UniversFacade.generate_summary(name, description)
                imagePathUrl = UniversFacade.generate_and_save_image(name, summary)

                UniversFacade.save_univers_to_database(name, description, imagePathUrl, utilisateur_id)

                response_data = {
                    'message': 'Univers créé avec succès',
                    'description': description,
                    'summary': summary,
                    'imagePathUrl': imagePathUrl
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
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

    @staticmethod
    def generate_univers_description(name):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "assistant", "content": "You are an expert in creating descriptions for fictional universe."},
                {"role": "user", "content": f"Generate a description for the universe {name},  less 500 characters."}
            ]
        )
        description = response.choices[0].message.content

        return description

    @staticmethod
    def generate_summary(name, description):
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "assistant", "content": "You are an expert with extensive knowledge about the {name} universe"},
                {"role": "user", "content": f"Generate a summary of the description {description} to create a Text-to-Image prompt for the {name} universe in under 200 characters."}
            ],
        )
        summary = response.choices[0].message.content

        return summary

    @staticmethod
    def generate_and_save_image(name, summary):
        try:
            # Créez un prompt pour générer une image
            prompt = f"Generate an image of the univers {name} with the following summary: {summary}"

            # Appelez l'API Text-to-Image pour générer l'image
            r = requests.post('https://clipdrop-api.co/text-to-image/v1',
                              files={'prompt': (None, prompt, 'text/plain')},
                              headers={'x-api-key': clipdrop_api_key}
            )

            if r.ok:
                # Le reste de votre code pour enregistrer l'image, enregistrer le chemin, etc.
                image_data = r.content

                # Enregistrez l'image sur le serveur avec un nom unique
                image_path = f"media/img/univers/{name}.png"  # Utilisez un nom unique basé sur le nom de l'univers
                with open(image_path, 'wb') as image_file:
                    image_file.write(image_data)

                # Retournez le chemin de l'image
                return image_path
            else:
                raise Exception(f'Erreur lors de la génération de l\'image: {r.status_code} - {r.text}')
        except Exception as e:
            # Vous pouvez gérer les erreurs ici ou les propager plus haut
            raise e


    @staticmethod
    def save_univers_to_database(name, description, imagePathUrl, utilisateur_id):
        try:
            with connection.cursor() as cursor:
                # Utilisez la méthode execute pour insérer les données dans la base de données
                cursor.execute("INSERT INTO univers (name, description, imagePathUrl, id_utilisateur) VALUES (%s, %s, %s, %s)",
                               [name, description, imagePathUrl, utilisateur_id])

            # Vous pouvez gérer le résultat ici si nécessaire
        except Exception as e:
            # Vous pouvez gérer les erreurs ici ou les propager plus haut
            raise e

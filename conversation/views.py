from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection

from authentification.utils import *

# Importez votre fonction `validate_jwt_token` depuis l'extrait de code que vous avez fourni.

class ConversationCreationView(APIView):
    def post(self, request):
        try:
            # Validez le jeton JWT de l'utilisateur
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                # L'utilisateur authentifié peut créer une conversation

                data = request.data  # Utilisez request.data pour récupérer les données de la requête au format JSON
                name = data.get('name')
                description = data.get('description')
                imgUrl = data.get('imgUrl')
                id_personnage = data.get('id_personnage')
                id_utilisateur = utilisateur_id  # L'ID de l'utilisateur authentifié
                id_univers = data.get('id_univers')

                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO conversation (name, description, imgUrl, id_personnage, id_utilisateur, id_univers) VALUES (%s, %s, %s, %s, %s, %s)",
                                   [name, description, imgUrl, id_personnage, id_utilisateur, id_univers])

                    conversation_id = cursor.lastrowid

                response_data = {
                    'message': 'Conversation créée avec succès'
                }

                return Response(response_data, status=status.HTTP_201_CREATED)

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

class ConversationListeView(APIView):
    def get(self, request):
        try:
            # Validez le jeton JWT de l'utilisateur
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                # L'utilisateur authentifié peut accéder à la liste de ses conversations

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, name, description, imgUrl, id_personnage, id_utilisateur, id_univers FROM conversation WHERE id_utilisateur = %s", [utilisateur_id])
                    result = cursor.fetchall()

                conversations = []
                for row in result:
                    conversation_info = {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'imgUrl': row[3],
                        'id_personnage': row[4],
                        'id_utilisateur': row[5],
                        'id_univers': row[6]
                    }
                    conversations.append(conversation_info)

                return Response({'conversations': conversations}, status=status.HTTP_200_OK)

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
        


class ConversationSuppView(APIView):
    def delete(self, request, conversation_id):
        try:
            # Validez le jeton JWT de l'utilisateur
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                # L'utilisateur authentifié peut supprimer une conversation

                with connection.cursor() as cursor:
                    # Vérifiez d'abord si la conversation appartient à l'utilisateur authentifié
                    cursor.execute("SELECT id FROM conversation WHERE id = %s AND id_utilisateur = %s", [conversation_id, utilisateur_id])
                    result = cursor.fetchone()

                    if result:
                        # La conversation appartient à l'utilisateur, nous pouvons la supprimer
                        cursor.execute("DELETE FROM conversation WHERE id = %s", [conversation_id])
                        return Response({'message': 'Conversation supprimée avec succès'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Conversation non trouvée ou ne vous appartient pas'}, status=status.HTTP_404_NOT_FOUND)

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
        

class ConversationDetailView(APIView):
    def get(self, request, conversation_id):
        try:
            # Validez le jeton JWT de l'utilisateur
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                with connection.cursor() as cursor:
                    # Sélectionnez la conversation, le personnage et l'univers liés à l'ID de la conversation
                    cursor.execute("SELECT c.id, c.name, c.description, c.imgUrl, c.id_personnage, c.id_utilisateur, c.id_univers, p.name as personnage_name, u.name as univers_name FROM conversation c JOIN personnage p ON c.id_personnage = p.id JOIN univers u ON c.id_univers = u.id WHERE c.id = %s", [conversation_id])
                    result = cursor.fetchone()

                if result:
                    # Vérifiez si l'utilisateur est le propriétaire de la conversation
                    if result[5] == utilisateur_id:
                        conversation_info = {
                            'id': result[0],
                            'name': result[1],
                            'description': result[2],
                            'imgUrl': result[3],
                            'id_personnage': result[4],
                            'id_utilisateur': result[5],
                            'id_univers': result[6],
                            'personnage_name': result[7],
                            'univers_name': result[8]
                        }
                        return Response({'conversation': conversation_info}, status=status.HTTP_200_OK)
                    else:
                        return Response({'error': 'Cette conversation ne vous appartient pas'}, status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response({'error': 'Conversation non trouvée'}, status=status.HTTP_404_NOT_FOUND)
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
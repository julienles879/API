from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection
from api.utils import *



class ConversationCreationView(APIView):
    def post(self, request):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                data = request.data  
                name = data.get('name')
                description = data.get('description')
                imgUrl = data.get('imgUrl')
                id_personnage = data.get('id_personnage')
                id_utilisateur = utilisateur_id 
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
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, name, description, imgUrl, id_personnage, id_utilisateur, id_univers FROM conversation WHERE id_utilisateur = %s", [utilisateur_id])
                    result = cursor.fetchall()

                conversations = []
                for row in result:
                    conversation_info = {
                        'id': row['id'],
                        'name': row['name'],
                        'description': row['description'],
                        'imgUrl': row['imgUrl'],
                        'id_personnage': row['id_personnage'],
                        'id_utilisateur': row['id_utilisateur'],
                        'id_univers': row['id_univers']
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
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                with connection.cursor() as cursor:

                    cursor.execute("SELECT id FROM conversation WHERE id = %s AND id_utilisateur = %s", [conversation_id, utilisateur_id])
                    result = cursor.fetchone()

                    if result:
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
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT c.id, c.name, c.description, c.imgUrl, c.id_personnage, c.id_utilisateur, c.id_univers, p.name as personnage_name, u.name as univers_name FROM conversation c JOIN personnage p ON c.id_personnage = p.id JOIN univers u ON c.id_univers = u.id WHERE c.id = %s", [conversation_id])
                    result = cursor.fetchone()

                if result:
                    if result[5] == utilisateur_id:
                        conversation_info = {
                            'id': result['id'],
                            'name': result['name'],
                            'description': result['description'],
                            'imgUrl': result['imgUrl'],
                            'id_personnage': result['id_personnage'],
                            'id_utilisateur': result['id_utilisateur'],
                            'id_univers': result['id_univers'],
                            'personnage_name': result['personnage_name'],
                            'univers_name': result['univers_name']
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
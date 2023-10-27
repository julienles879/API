from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection

from authentification.utils import *


class MessageCreationView(APIView):
    def post(self, request, id_conversation):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                data = request.data

                date = data.get('date')
                text = data.get('text')
                id_conversation = data.get('id_conversation')

                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO message (date, text, id_conversation) VALUES (%s, %s, %s)",
                                   [date, text, id_conversation])

                    message_id = cursor.lastrowid

                response_data = {
                    'message': 'Message envoyé avec succès',
                    'id': message_id,
                    'date': date,
                    'text': text,
                    'id_conversation': id_conversation
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


class MessageHistoriqueView(APIView):
    def get(self, request, id_conversation):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, date, text FROM message WHERE id_conversation = %s", [id_conversation])
                    result = cursor.fetchall()

                messages = []
                for row in result:
                    message_info = {
                        'id': row[0],
                        'date': row[1],
                        'text': row[2],
                    }
                    messages.append(message_info)

                return Response({'messages': messages}, status=status.HTTP_200_OK)

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
        
class MessageDernierView(APIView):
    def get(self, request, id_conversation):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, date, text FROM message WHERE id_conversation = %s ORDER BY date DESC LIMIT 1", [id_conversation])
                    result = cursor.fetchone()

                if result:
                    dernier_message = {
                        'id': result[0],
                        'date': result[1],
                        'text': result[2],
                    }
                    return Response({'dernier_message': dernier_message}, status=status.HTTP_200_OK)
                else:
                    return Response({'dernier_message': None, 'message': 'Aucun message trouvé dans la conversation'}, status=status.HTTP_404_NOT_FOUND)

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
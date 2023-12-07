from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from datetime import datetime
from django.db import connection
from api.utils import *
import openai
import os


# Vue qui permet de créer un personnage
class MessageCreationView(APIView):

    # vue post qui permet de créer un message
    def post(self, request, id_conversation):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                data = request.data

                date_time = data.get('date_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                text = data.get('text')
                id_conversation = data.get('id_conversation')

                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO message (date_time, text, id_conversation) VALUES (%s, %s, %s)",
                                   [date_time, text, id_conversation])

                    message_id = cursor.lastrowid

                response_data = {
                    'message': 'Message envoyé avec succès',
                    'id': message_id,
                    'date_time': date_time,
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


# Vue qui permet d'accéder à l'historique de la conversation
class MessageHistoriqueView(APIView):

    # Vue get qui récupére l'historique
    def get(self, request, id_conversation):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, date_time, text, api_response FROM message WHERE id_conversation = %s", [id_conversation])
                    result = cursor.fetchall()
                
                messages = []
                for row in result:
                    message_info = {
                        'id': row[0],
                        'date_time': row[1],
                        'text': row[2],
                        'api_response': row[3]
                    }
                    messages.append(message_info)
                print(messages)
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
        

# Vue qui permet d'afficher le derniers message        
class MessageDernierView(APIView):

    # Vue get qui permet d'accéder au dernier message
    def get(self, request, id_conversation):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, date_time, text FROM message WHERE id_conversation = %s ORDER BY date_time DESC LIMIT 1", [id_conversation])
                    result = cursor.fetchone()

                if result:
                    dernier_message = {
                        'id': result[0],
                        'date_time': result[1],
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


# Vue qui permet de répondre au dernier message        
class RepondreAuDernierMessageView(APIView):

    # Vue post permettant de créer un message de réponse
    def post(self, request, id_conversation):
        try:
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, date_time, text FROM message WHERE id_conversation = %s ORDER BY date_time DESC LIMIT 1", [id_conversation])
                    result = cursor.fetchone()

                    if result:
                        dernier_message = {
                            'id': result[0],
                            'date_time': result[1],
                            'text': result[2],
                        }
                        dernier_message_text = dernier_message['text']

                        cursor.execute("SELECT id, date_time, text, api_response FROM message WHERE id_conversation = %s ORDER BY date_time", [id_conversation])
                        historique_messages = cursor.fetchall()

                        conversation_history = []
                        for message in historique_messages:
                            conversation_history.append({
                                "role": "user",
                                "content": message[2]
                            })

                        conversation_history.append({
                            "role": "user",
                            "content": dernier_message_text
                        })    
                        cursor.execute("SELECT id, id_personnage, id_univers FROM conversation WHERE id = %s", [id_conversation])
                        result = cursor.fetchone()
                        personnage_id = result[0]
                        univers_id = result[1]
                        print('result: ', result)
                        print("SELECT id, id_personnage, id_univers FROM conversation WHERE id = %s", [id_conversation])

                        cursor.execute("SELECT name, description FROM personnage WHERE id = %s", [personnage_id])
                        result = cursor.fetchone()
                        personnage_name = result[0]
                        personnage_description = result[1]
                        print('result: ', result)
                        print("SELECT name, description FROM personnage WHERE id = %s", [personnage_id])


                        cursor.execute("SELECT name FROM univers WHERE id = %s", [univers_id])
                        result = cursor.fetchone()
                        univers_name = result[0]
                        
                        print("SELECT name FROM univers WHERE id = %s", [univers_id])
                        message_assistant = f"In the context of a role-playing game, the AI becomes the character {personnage_name} from the universe {univers_name} and responds to the human.\n\nHere is the description of the character {personnage_description}:\n---\n{dernier_message_text}"
                        
                        print('message : ',message_assistant)
                        response = openai.chat.completions.create(
                            model="gpt-3.5-turbo-1106",
                            messages=[
                                {"role": "assistant", "content": message_assistant},
                                {"role": "user", "content": dernier_message_text},
                            ]
                        )

                        print(response)
                        api_response = response.choices[0].message.content

                        cursor.execute("UPDATE message SET api_response = %s WHERE id = %s", [api_response, dernier_message['id']])

                        connection.commit()

                        return Response({'dernier_message': dernier_message, 'reponse': api_response}, status=status.HTTP_200_OK)
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

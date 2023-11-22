from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection

from api.database import *
from api.utils import *



db_connexion = DatabaseConnexion()


class UtilisateurListeView(APIView):
    def get(self, request):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
            print('token : ', token)

            utilisateur_id, username = validate_jwt_token(token)

            if utilisateur_id is not None:

                print(utilisateur_id)

                with db_connexion.connection.cursor() as cursor:
                    cursor.execute("SELECT id, username, email FROM utilisateur")
                    result = cursor.fetchall()

                users = []

                for row in result:

                    user_info = {
                        'id': row['id'],
                        'username': row['username'],
                        'email': row['email'],
                    }

                    users.append(user_info)

                return Response({'users': users}, status=status.HTTP_200_OK)
            else:
                error_response = {
                    'error': 'Token invalide'
                }
                return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        except (DecodeError, ExpiredSignatureError) as e:
            error_response = {
                'error': str(e)
            }
            print(error_response)
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            error_response = {
                'error': str(e)
            }
            print(error_response)
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)




class UtilisateurDetailView(APIView):
    def get(self, request, utilisateur_id):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]

            validated_utilisateur_id, username = validate_jwt_token(token)
            if validated_utilisateur_id is not None:

                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, username, email FROM utilisateur WHERE id = %s", [utilisateur_id])
                    result = cursor.fetchone()

                if result:
                    user_info = {
                        'id': result[0],
                        'username': result[1],
                        'email': result[2],
                    }
                    return Response({'user': user_info}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)
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


class UtilisateurModificationView(APIView):
    def put(self, request, utilisateur_id):
        try:
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]

            validated_utilisateur_id, username = validate_jwt_token(token)
            if validated_utilisateur_id is not None:

                data = request.data
                new_username = data.get('username')
                new_email = data.get('email')

                with connection.cursor() as cursor:
                    cursor.execute("UPDATE utilisateur SET username = %s, email = %s WHERE id = %s",
                                   [new_username, new_email, utilisateur_id])

                if cursor.rowcount > 0:
                    return Response({'message': 'Utilisateur mis à jour avec succès'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Utilisateur non trouvé'}, status=status.HTTP_404_NOT_FOUND)

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

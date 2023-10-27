from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection


from authentification.utils import *





# Importez votre fonction `validate_jwt_token` depuis l'extrait de code que vous avez fourni.

class UtilisateurListeView(APIView):
    def get(self, request):
        try:
            # Récupérez le jeton JWT depuis l'en-tête d'autorisation
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]

            # Validez le jeton JWT
            utilisateur_id, username = validate_jwt_token(token)
            if utilisateur_id is not None:
                # Vous avez validé le jeton avec succès, vous pouvez maintenant exécuter votre requête SQL pour obtenir la liste des utilisateurs
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, username, email FROM utilisateur")
                    result = cursor.fetchall()

                # Construisez la liste des utilisateurs
                users = []
                for row in result:
                    user_info = {
                        'id': row[0],
                        'username': row[1],
                        'email': row[2],
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
            return Response(error_response, status=status.HTTP_401_UNAUTHORIZED)

        except Exception as e:
            error_response = {
                'error': str(e)
            }
            return Response(error_response, status=status.HTTP_400_BAD_REQUEST)




# Importez votre fonction `validate_jwt_token` depuis l'extrait de code que vous avez fourni.

class UtilisateurDetailView(APIView):
    def get(self, request, utilisateur_id):
        try:
            # Récupérez le jeton JWT depuis l'en-tête d'autorisation
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]

            # Validez le jeton JWT
            validated_utilisateur_id, username = validate_jwt_token(token)
            if validated_utilisateur_id is not None:
                # Vous avez validé le jeton avec succès, vous pouvez maintenant exécuter votre requête SQL pour obtenir les détails de l'utilisateur

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



# Importez votre fonction `validate_jwt_token` depuis l'extrait de code que vous avez fourni.

class UtilisateurModificationView(APIView):
    def put(self, request, utilisateur_id):
        try:
            # Récupérez le jeton JWT depuis l'en-tête d'autorisation
            token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]

            # Validez le jeton JWT
            validated_utilisateur_id, username = validate_jwt_token(token)
            if validated_utilisateur_id is not None:
                # Vous avez validé le jeton avec succès, vous pouvez maintenant exécuter votre requête SQL pour mettre à jour l'utilisateur

                # Récupérez les données à mettre à jour depuis la demande
                data = request.data
                new_username = data.get('username')
                new_email = data.get('email')

                with connection.cursor() as cursor:
                    cursor.execute("UPDATE utilisateur SET username = %s, email = %s WHERE id = %s",
                                   [new_username, new_email, utilisateur_id])

                # Vérifiez si la mise à jour a réussi
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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection

from authentification.utils import *


class UniversCreationView(APIView):
    def post(self, request):
        try:
            # Validez le jeton JWT
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                # L'utilisateur authentifié peut créer un univers

                data = request.data  # Utilisez request.data pour récupérer les données de la requête au format JSON
                name = data.get('name')
                description = data.get('description')
                imagePathUrl = data.get('imagePathUrl')

                # Exécutez une requête SQL pour insérer l'univers dans la base de données
                with connection.cursor() as cursor:
                    cursor.execute("INSERT INTO univers (name, description, imagePathUrl, id_utilisateur) VALUES (%s, %s, %s, %s)",
                                   [name, description, imagePathUrl, utilisateur_id])

                response_data = {
                    'message': 'Univers créé avec succès'
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


class UniversListeView(APIView):
    def get(self, request):
        try:
            # Validez le jeton JWT
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                # L'utilisateur authentifié peut accéder à la liste des univers

                # Exécutez une requête SQL pour récupérer la liste des univers
                with connection.cursor() as cursor:
                    cursor.execute("SELECT id, name, description, imagePathUrl, id_utilisateur FROM univers")
                    result = cursor.fetchall()

                # Construisez la liste des univers
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
            # Validez le jeton JWT
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                # L'utilisateur authentifié peut accéder au détail de l'univers

                # Exécutez une requête SQL pour récupérer les détails de l'univers
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
            # Validez le jeton JWT
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                # L'utilisateur authentifié peut modifier l'univers

                data = request.data  # Utilisez request.data pour récupérer les données de la requête au format JSON
                name = data.get('name')
                description = data.get('description')
                imagePathUrl = data.get('imagePathUrl')

                # Exécutez une requête SQL pour mettre à jour l'univers dans la base de données
                with connection.cursor() as cursor:
                    cursor.execute("UPDATE univers SET name = %s, description = %s, imagePathUrl = %s WHERE id = %s AND id_utilisateur = %s",
                                   [name, description, imagePathUrl, univers_id, utilisateur_id])

                # Vérifiez si l'univers a été modifié avec succès
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
        

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jwt.exceptions import DecodeError, ExpiredSignatureError
from django.db import connection

from authentification.utils import *

# Importez votre fonction `validate_jwt_token` depuis l'extrait de code que vous avez fourni.

class UniversSuppView(APIView):
    def delete(self, request, univers_id):
        try:
            # Validez le jeton JWT
            utilisateur_id, username = validate_jwt_token(request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1])
            if utilisateur_id is not None:
                # L'utilisateur authentifié peut supprimer l'univers

                # Exécutez une requête SQL pour supprimer l'univers de la base de données
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM univers WHERE id = %s AND id_utilisateur = %s",
                                   [univers_id, utilisateur_id])

                # Vérifiez si l'univers a été supprimé avec succès
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
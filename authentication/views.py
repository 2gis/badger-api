from django.contrib.auth import authenticate, login, logout
from rest_framework import status, views
from rest_framework.response import Response
from authentication.serializers import AccountSerializer
from testreport.models import ExtUser

import logging
log = logging.getLogger(__name__)


class LoginView(views.APIView):

    def post(self, request, format=None):
        username = request.data.get('username', None)
        password = request.data.get('password', None)
        account = authenticate(username=username, password=password)
        if account is not None:
            if account.is_active:
                if not hasattr(account, 'settings'):
                    account.settings = ExtUser()
                    account.settings.save()
                login(request, account)
                serialized = AccountSerializer(account)
                return Response(serialized.data)
            else:
                return Response({
                    'status': 'Unauthorized',
                    'message': 'This account has been disabled.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Authentication failed'
            }, status=status.HTTP_401_UNAUTHORIZED)


class IsAuthorizedView(views.APIView):

    def get(self, request, format=None):
        if request.user.is_authenticated():
            return Response(AccountSerializer(request.user).data,
                            status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Unauthorized'
            }, status=status.HTTP_401_UNAUTHORIZED)


class UpdateSettingsView(views.APIView):

    def post(self, request):
        if request.user.is_authenticated():
            if not request.data:
                return Response({
                    'message': 'Incorrect data in request'
                }, status=status.HTTP_400_BAD_REQUEST)
            for key, value in request.data.items():
                if hasattr(request.user.settings, key):
                    if key == 'dashboards':
                        request.user.settings.set_dashboards(value)
                    else:
                        setattr(request.user.settings, key, value)
                request.user.settings.save()
            return Response({
                'message': 'Profile settings successfully updated'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Unauthorized'
            }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(views.APIView):

    def get(self, request, format=None):
        if request.user.is_authenticated():
            logout(request)
            return Response({
                'status': 'Success',
                'message': 'Logout done.'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'status': 'Unauthorized',
                'message': 'Unauthorized'
            }, status=status.HTTP_401_UNAUTHORIZED)

from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, routers, generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')
    if not username or not password:
        return Response({'error': 'Username and password required'}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({'error': 'Username already exists'}, status=400)
    user = User.objects.create_user(username=username, email=email, password=password)
    return Response({'id': user.id, 'username': user.username}, status=201)

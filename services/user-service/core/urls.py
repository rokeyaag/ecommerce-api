from django.urls import path
from django.contrib.auth.models import User
from rest_framework import serializers, viewsets, routers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

router = routers.DefaultRouter()
router.register('', UserViewSet)

urlpatterns = router.urls

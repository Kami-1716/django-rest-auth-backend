from rest_framework.serializers import ModelSerializer
from . import models


class Auth0UserSerializer(ModelSerializer):
    class Meta:
        model = models.Auth0User
        fields = '__all__'




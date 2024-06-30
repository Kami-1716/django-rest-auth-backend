from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Auth0User
from .serializers import Auth0UserSerializer  # Import your serializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_new_user(request):
    try:
        auth0Id = request.data['auth0Id']
        already_exists = Auth0User.objects.filter(auth0Id=auth0Id).first()
        if already_exists:
            serializer = Auth0UserSerializer(already_exists)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        serializer = Auth0UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response('Missing required field', status=status.HTTP_400_BAD_REQUEST)


from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from .models import Auth0User
from .serializers import Auth0UserSerializer

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user(request):
    user_id = request.user.user_id

    if not user_id:
        return Response({'message': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        user = Auth0User.objects.get(id=user_id)
    except Auth0User.DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = Auth0UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

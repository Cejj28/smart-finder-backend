from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from .models import Item
from .serializers import ItemSerializer, UserSerializer, StudentRegisterSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": token.key
        }, status=status.HTTP_201_CREATED)

class StudentRegisterView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = StudentRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff,
            'full_name': user.get_full_name(),
        }, status=status.HTTP_201_CREATED)

class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # We allow both username or email in the 'username' field
        identifier = request.data.get('username')
        password = request.data.get('password')

        # Check if the identifier is an email
        if '@' in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
                # If found, use the actual username for authentication
                request.data['username'] = user_obj.username
            except User.DoesNotExist:
                pass # Let it fail normally in authentication if not found

        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
            'is_staff': user.is_staff
        })

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all().order_by('-created_at')
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        # All mobile users (including admins) see only Approved items in the public feed
        # Admins manage pending reports through the web admin panel
        queryset = self.queryset.filter(status='Approved')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(reporter=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.reporter != request.user and not request.user.is_staff:
            return Response({'error': 'You do not have permission to delete this item.'}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.reporter != request.user and not request.user.is_staff:
            return Response({'error': 'You do not have permission to edit this item.'}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def my_posts(self, request):
        # Always return ALL of the user's own posts regardless of status
        queryset = self.queryset.filter(reporter=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

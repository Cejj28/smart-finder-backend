from rest_framework import viewsets, generics, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth.models import User
from .models import Item, Claim, Notification
from .serializers import (
    ItemSerializer, UserSerializer, StudentRegisterSerializer, 
    ClaimSerializer, NotificationSerializer, UserProfileSerializer, 
    ChangePasswordSerializer
)

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'status': 'notification marked as read'})

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'status': 'all notifications marked as read'})

from django.core.management import call_command
from django.http import JsonResponse

def trigger_migration(request):
    try:
        call_command('migrate')
        return JsonResponse({'status': 'success', 'message': 'Database migrated successfully!'})
    except Exception as e:
        import traceback
        return JsonResponse({'status': 'error', 'message': str(e), 'details': traceback.format_exc()})

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user

        # Check current password
        if not user.check_password(serializer.data.get("current_password")):
            return Response({"current_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)

        # Set new password
        user.set_password(serializer.data.get("new_password"))
        user.save()
        return Response({"status": "password updated successfully"})

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
        # Admins on the web see everything; Students/Mobile users see only Approved
        if request.user.is_staff and request.query_params.get('admin') == 'true':
            # Use a fresh queryset to bypass any caching issues
            queryset = Item.objects.all().order_by('-created_at')
        else:
            queryset = Item.objects.filter(status='Approved').order_by('-created_at')
        
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

    @action(detail=True, methods=['get'])
    def matches(self, request, pk=None):
        """
        Smart Match AI Logic:
        Finds potential matches based on opposite type and same category.
        """
        item = self.get_object()
        target_type = 'Found' if item.type == 'Lost' else 'Lost'
        
        # Base queryset: items of the opposite type that aren't reported by the same person
        queryset = Item.objects.filter(type=target_type).exclude(reporter=item.reporter)

        # 1. Try matching by category if it exists
        if item.category:
            queryset = queryset.filter(category=item.category)
        else:
            # 2. Fallback: Match by item name (case-insensitive partial match)
            # This ensures the UI appears during testing even if ML hasn't run
            queryset = queryset.filter(item_name__icontains=item.item_name[:5])

        # Exclude the current item just in case (though types should handle it)
        queryset = queryset.exclude(id=item.id)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class ClaimViewSet(viewsets.ModelViewSet):
    queryset = Claim.objects.all().order_by('-created_at')
    serializer_class = ClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        try:
            # Admins see all claims, users see only their own
            if request.user.is_staff:
                queryset = Claim.objects.all().order_by('-created_at')
            else:
                queryset = Claim.objects.filter(user=request.user).order_by('-created_at')
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(error_details)
            return Response({'error': str(e), 'details': error_details}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        # If the user is authenticated, link the claim to them.
        # If the claimant_name is empty, use the user's full name or username.
        user = self.request.user
        claimant_name = self.request.data.get('claimant_name')
        if not claimant_name and user.is_authenticated:
            claimant_name = user.get_full_name() or user.username
        
        serializer.save(user=user, claimant_name=claimant_name)

    def perform_update(self, serializer):
        instance = serializer.save()
        # If the claim is released, mark the item as released so it hides from public feeds
        if instance.status == 'Released':
            instance.item.status = 'Released'
            instance.item.save()

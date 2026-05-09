from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, UserViewSet, RegisterView, CustomAuthToken, StudentRegisterView, ClaimViewSet, trigger_migration, NotificationViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'users', UserViewSet)
router.register(r'claims', ClaimViewSet)
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('trigger-migration/', trigger_migration, name='trigger_migration'),
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/student/', StudentRegisterView.as_view(), name='register-student'),
    path('login/', CustomAuthToken.as_view(), name='login'),
]

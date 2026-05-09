from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, UserViewSet, RegisterView, CustomAuthToken, StudentRegisterView, ClaimViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'users', UserViewSet)
router.register(r'claims', ClaimViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('register/student/', StudentRegisterView.as_view(), name='register-student'),
    path('login/', CustomAuthToken.as_view(), name='login'),
]

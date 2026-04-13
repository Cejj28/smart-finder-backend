from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ItemViewSet, UserViewSet, RegisterView, CustomAuthToken

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomAuthToken.as_view(), name='login'),
]

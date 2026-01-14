from django.urls import path
from .views import FetchUsersAPIView, GetProcessedUsersAPIView, UserCreateAPIView, getexternaldata
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/users/', UserCreateAPIView.as_view(), name='create_user'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/getusers/', FetchUsersAPIView.as_view(), name='get_users'),
    path('api/getprocesseddata/', GetProcessedUsersAPIView.as_view(), name='get_processed_data'),
    path('api/externaldata/', getexternaldata),
]

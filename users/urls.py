from django.urls import path
from .views import FetchUsersAPIView, GetProcessedUsersAPIView, RemoveScheduledTask, SceduleTask, UserCreateAPIView, dashboard, getexternaldata, login_view, start_login_celery, start_login_playwright
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
    path('api/scheduletask/', SceduleTask.as_view()),
    path('api/removescheduletask/', RemoveScheduledTask.as_view()),
    path("login/", login_view),
    path("dashboard/", dashboard),
    path("api/startlogin/", start_login_playwright),
    path("api/startlogincelery/", start_login_celery),
]

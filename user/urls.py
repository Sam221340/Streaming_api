from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import *

router = routers.DefaultRouter()
router.register(r'users', UserRegistrationView, basename='users')
router.register(r'teams', TeamViewSet, basename='teams')
# router.register(r'like_count', HighlightLikeViewset, basename='like_count')
router.register(r'highlights', HighlightsviewSet, basename='highlights')
router.register(r'player', PlayerViewSet, basename='player')
router.register(r'match', MatchViewSet, basename='match')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('change-password/', UserChangePasswordView.as_view(), name='pass-change'),
    path('reset-password/', UserResetPasswordView.as_view(), name='reset'),
    path("role_assign/", RolesAssignment.as_view(), name='role-assignment'),
    path('passresetini/', UserResetPasswordInitiate.as_view(), name='passresetini'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh-token/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('teams/', TeamListCreateAPIView.as_view(), name='team-list'),
    # path('teams/<int:pk>/', TeamDetailView.as_view(), name='team-detail'),
]

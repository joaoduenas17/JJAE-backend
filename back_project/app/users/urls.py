from django.urls import path

from rest_framework import routers
from users import views
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'users'

router = routers.SimpleRouter()
router.register('users', views.UserViewSet, basename='users')
router.register(r'passwords', views.ResetPasswordView, basename='passwords')
urlpatterns = router.urls

urlpatterns += [
    path('login/', views.AuthTokenViewSet.as_view(), name='login'),
    path('refresh-token/', TokenRefreshView.as_view(), name='refresh'),
    path('user/register/', views.UserViewSet.as_view({'post': 'create'}), name='users-register')
]

from rest_framework import routers

from clients.views import ClientViewSet

router = routers.SimpleRouter()

router.register(r'client', ClientViewSet, basename='client')

urlpatterns = router.urls

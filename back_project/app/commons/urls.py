from rest_framework import routers

from commons.views import CommonsViewSet

router = routers.SimpleRouter()

router.register(r'commons', CommonsViewSet, basename='commons')

urlpatterns = router.urls
from django.conf.urls import url, include
from HRMS_website import views

urlpatterns = [
    url(r'^', include(router.urls)),
]


# Login and logout views for the browsable API
urlpatterns += [
    url(r'^auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
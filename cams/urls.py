from django.urls import path, include
from rest_framework.routers import DefaultRouter

from cams import views

router = DefaultRouter()
router.register(r'cams', views.ChannelViewSet)

urlpatterns = [
    path('image_stream/<int:channel_id>/', views.image_stream, name='image_stream'),
    path('', include(router.urls)),
]

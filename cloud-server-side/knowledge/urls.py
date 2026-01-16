from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, DocumentViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'documents', DocumentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

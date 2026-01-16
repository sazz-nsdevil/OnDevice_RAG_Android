from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GradeViewSet, SubjectViewSet, DocumentViewSet, VectorSnapshotViewSet

router = DefaultRouter()
router.register(r'grades', GradeViewSet)
router.register(r'subjects', SubjectViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'snapshots', VectorSnapshotViewSet)

urlpatterns = [
    path('', include(router.urls)),
]

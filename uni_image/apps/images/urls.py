from django.conf.urls import url
from apps.images.views import ImageCategoryViewSet, ImagesAllViewSet, ImagesViewSet, CollectionViewSet, \
    UploadLocationViewSet

from rest_framework.routers import DefaultRouter

urlpatterns = [
    url(r'^upload_location/', UploadLocationViewSet.as_view()),
]

router = DefaultRouter()
router.register(r'image_category', ImageCategoryViewSet, base_name='image_category')
router.register(r'image_all', ImagesAllViewSet, base_name='image_all')
router.register(r'image', ImagesViewSet, base_name='image')
router.register(r'collection', CollectionViewSet, base_name='collection')

urlpatterns += router.urls

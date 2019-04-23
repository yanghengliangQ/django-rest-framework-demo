from django.contrib.auth import get_user_model
from rest_framework.views import APIView

from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from apps.images.models import ImageCategory, Images, Collection, Location
from .serializers import ImageCategorySerializer, ImagesListSerializer, ImagesSerializer, CollectionSerializer, \
    CollectionCreateSerializer, ImagesAllListSerializer

User = get_user_model()


class ImageCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    """
    图片类型管理
    """
    permission_classes = [AllowAny]
    pagination_class = None

    queryset = ImageCategory.objects.all()
    serializer_class = ImageCategorySerializer


class ImagesAllViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    图片列表
    """
    queryset = Images.objects.all()
    permission_classes = [AllowAny]
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('image_type',)
    ordering_fields = ('add_time', 'click_num')

    def retrieve(self, request, *args, **kwargs):
        """
        点击数 + 1
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        instance = self.get_object()
        instance.click_num += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action == "list":
            return ImagesAllListSerializer
        return ImagesSerializer


class ImagesViewSet(viewsets.ModelViewSet):
    """
    图片管理
    """

    def get_serializer_class(self):
        if self.action == "list":
            return ImagesListSerializer
        return ImagesSerializer

    def get_queryset(self):
        return Images.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data['user'] = self.request.user.id
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CollectionViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                        viewsets.GenericViewSet):
    """
    我的收藏管理
    """

    def get_serializer_class(self):
        if self.action == "create":
            return CollectionCreateSerializer
        return CollectionSerializer

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data['user'] = self.request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UploadLocationViewSet(APIView):
    """
    登陆位置
    """

    def post(self, request):
        if request.data.__contains__('longitude') and request.data.__contains__('latitude') and \
                request.data.__contains__('name') and request.data.__contains__('address') and \
                request.data.__contains__('image'):
            image = Images.objects.get(id=request.data['image'])
            Location.objects.create(image=image, longitude=request.data['longitude'],
                                    latitude=request.data['latitude'], name=request.data['name'],
                                    address=request.data['address'])
            return Response(status=status.HTTP_200_OK, data={'status_code': 0, 'error': ''})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '请求参数错误'})

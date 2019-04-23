from rest_framework import serializers
from django.contrib.auth import get_user_model
from apps.images.models import ImageCategory, Images, Collection, Location

from math import radians, cos, sin, asin, sqrt

User = get_user_model()


def geodistance(lng1, lat1, lng2, lat2):
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    dis = 2 * asin(sqrt(a)) * 6371 * 1000
    return dis


class ImageCategorySerializer(serializers.ModelSerializer):
    """
    图片类型管理
    """

    class Meta:
        model = ImageCategory
        fields = ("id", "name")


class LocationSerializer(serializers.ModelSerializer):
    """
    地理位置
    """

    class Meta:
        model = Location
        fields = "__all__"


class ImagesAllListSerializer(serializers.ModelSerializer):
    """
    图片列表
    """
    image_type = serializers.ReadOnlyField(source='image_type.name')
    location = LocationSerializer()

    class Meta:
        model = Images
        fields = ("id", "image_type", "image", "name", "add_time", "click_num", "location")


class ImagesListSerializer(serializers.ModelSerializer):
    """
    图片列表
    """
    image_type = serializers.ReadOnlyField(source='image_type.name')
    location = LocationSerializer()
    distance = serializers.SerializerMethodField()

    def get_distance(self, obj):
        try:
            self_location = Location.objects.get(user=self.context["request"].user)
            image_location = Location.objects.get(image=obj)
            return geodistance(self_location.longitude, self_location.latitude, image_location.longitude,
                               image_location.latitude)
        except:
            return ''

    class Meta:
        model = Images
        fields = ("id", "image_type", "image", "name", "add_time", "click_num", "location", "distance")


class ImagesSerializer(serializers.ModelSerializer):
    """
    图片管理
    """
    click_num = serializers.ReadOnlyField()

    class Meta:
        model = Images
        fields = ("id", "user", "image_type", "name", "desc", "image", "click_num")


class CollectionSerializer(serializers.ModelSerializer):
    """
    收藏管理
    """
    image = ImagesListSerializer()

    class Meta:
        model = Collection
        fields = ("id", "image")


class CollectionCreateSerializer(serializers.ModelSerializer):
    """
    收藏管理
    """

    class Meta:
        model = Collection
        fields = ("user", "image")

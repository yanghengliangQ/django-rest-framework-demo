from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

User = get_user_model()


def user_directory_path(instance, filename):
    print("{0}/{1}/{2}".format(instance.image_type.id, instance.user.id, filename))
    return "{0}/{1}/{2}".format(instance.image_type.id, instance.user.id, filename)


class ImageCategory(models.Model):
    name = models.CharField(default="", max_length=30, verbose_name="类别名", help_text="类别名")
    desc = models.TextField(default="", verbose_name="类别描述", help_text="类别描述")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "图片类别"
        verbose_name_plural = verbose_name


class Images(models.Model):
    user = models.ForeignKey(User, verbose_name="归属用户")
    image_type = models.ForeignKey(ImageCategory, verbose_name="图片类型")
    name = models.CharField(max_length=20, default="", verbose_name="图片名称")
    desc = models.TextField(default="", verbose_name="图片描述", help_text="图片描述")
    image = models.ImageField(upload_to=user_directory_path, verbose_name="图片")
    click_num = models.IntegerField(default=0, verbose_name="点击数")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "图片"
        verbose_name_plural = verbose_name


class Collection(models.Model):
    user = models.ForeignKey(User, verbose_name="归属用户")
    image = models.ForeignKey(Images, verbose_name="收藏的图片")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "我的收藏"
        verbose_name_plural = verbose_name


class Location(models.Model):
    """
    地理位置
    """
    user = models.OneToOneField(User, null=True, blank=True, verbose_name="归属用户")
    image = models.OneToOneField(Images, null=True, blank=True, verbose_name="归属图片")
    name = models.CharField(max_length=50, default="", verbose_name="位置名称")
    address = models.CharField(max_length=100, default="", verbose_name="详细地址")
    latitude = models.FloatField(default=0, verbose_name="纬度")
    longitude = models.FloatField(default=0, verbose_name="经度")
    add_time = models.DateTimeField(auto_now=True, verbose_name="最近获取时间")

    class Meta:
        verbose_name = "地理位置"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

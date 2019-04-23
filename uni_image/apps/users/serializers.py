from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django_redis import get_redis_connection

from django.contrib.auth.hashers import make_password

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    注册个人用户序列化
    """
    verification_code = serializers.CharField(required=True, write_only=True, max_length=4, min_length=4, label="验证码",
                                              error_messages={
                                                  "blank": "请输入验证码",
                                                  "required": "请输入验证码",
                                                  "max_length": "验证码格式错误",
                                                  "min_length": "验证码格式错误"
                                              },
                                              help_text="验证码")
    username = serializers.CharField(label="用户名", help_text="用户名", required=True, allow_blank=False,
                                     validators=[UniqueValidator(queryset=User.objects.all(), message="用户已经存在")])

    password = serializers.CharField(
        style={'input_type': 'password'}, help_text="密码", label="密码", write_only=True,
    )

    def create(self, validated_data):
        user = super(UserRegisterSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        print(user.password)
        return user

    def validate(self, attrs):
        redis_key = 'VerificationCode_%s' % attrs['username']
        con = get_redis_connection("default")
        if not con.exists(redis_key):
            raise serializers.ValidationError('验证码已过期')
        value = con.get(redis_key)
        if value.decode('utf-8') != attrs['verification_code']:
            raise serializers.ValidationError('验证码错误')
        attrs["mobile"] = attrs["username"]
        del attrs["verification_code"]
        return attrs

    class Meta:
        model = User
        fields = ("username", "verification_code", "mobile", "password")


class UserDetailUpdateSerializer(serializers.ModelSerializer):
    """
    修改用户信息序列化类
    """

    class Meta:
        model = User
        fields = ("name", "birthday", "gender", "email")


class UserDetailRetrieveSerializer(serializers.ModelSerializer):
    """
    用户详情序列化类
    """

    class Meta:
        model = User
        fields = ("id", "name", "gender", "birthday", "email", "mobile")

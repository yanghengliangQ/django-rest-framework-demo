import re
from random import choice

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from django_redis import get_redis_connection

from rest_framework import authentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from rest_framework import mixins
from rest_framework import viewsets
from django.db.models import Q
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from uni_image.settings import APIKEY
from apps.utils.yunpian import YunPian

from .serializers import UserRegisterSerializer, UserDetailUpdateSerializer, UserDetailRetrieveSerializer
from apps.images.models import Location

from django.conf import settings

User = get_user_model()


class CustomBackend(ModelBackend):
    """
    自定义用户验证
    """

    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(mobile=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None


class SmsCodeViewset(APIView):
    permission_classes = [AllowAny]

    """
    发送短信验证码
    """

    def generate_code(self):
        """
        生成四位数字的验证码
        :return:
        """
        seeds = "1234567890"
        random_str = []
        for i in range(4):
            random_str.append(choice(seeds))

        return "".join(random_str)

    def post(self, request):
        """
        1、判断所需参数是否存在，如不存在则返回报错
        2、根据验证码类型进行判断，如果为注册验证码，则检查手机号是否已存在，如存在则报错，如果为找回密码验证码，则检查手机
        号是否已存在，如不存在则返回报错
        3、判断手机号是否在15分钟内已发送过验证码，如发送过则返回报错
        :param request:
        :return:
        """
        if not request.data.__contains__('mobile') or not request.data.__contains__('code_type'):
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '请求参数错误'})
        mobile = request.data['mobile']
        if not re.match(r'^1\d{10}$', mobile):
            return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '无效的手机号'})
        code_type = request.data['code_type']
        if code_type == 'register':
            # 注册
            if User.objects.filter(mobile=mobile):
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '该手机号已注册'})
        elif code_type == 'change_mobile':
            # 修改密码
            if User.objects.filter(mobile=mobile):
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '该手机号已注册'})
        elif code_type == 'retrieve_password':
            # 找回密码
            if not User.objects.filter(mobile=mobile):
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '该手机号未注册'})
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '请求参数错误'})
        redis_key = 'VerificationCode_%s' % mobile
        con = get_redis_connection("default")
        if con.exists(redis_key):
            return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '请勿重复获取验证码'})
        yun_pian = YunPian(APIKEY)
        code = self.generate_code()
        sms_status = yun_pian.send_sms(code=code, mobile=mobile)
        if sms_status["code"] != 0:
            return Response({
                "mobile": sms_status["msg"]
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            con.set(redis_key, code)
            con.expire(redis_key, getattr(settings, 'MOBILE_VERIFY_CODE_EXPIRE_SECONDS', 90000))
            return Response(status=status.HTTP_200_OK, data={'status_code': 0, 'error': ''})


class RegisterView(APIView):
    """
    用户注册
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        1、判断所需参数是否存在，如不存在则返回报错
        2、判断手机号是否注册，如已注册则返回报错
        3、判断验证是否过期，如已过期则返回报错
        4、判断验证码是否正确，如不正确则返回报错
        5、判断激活码是否存在，如不存在则返回报错
        :param request:
        :return:
        """
        serializer = UserRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED, data={'status_code': 0, 'error': ''})


class ChangePasswordView(APIView):
    """
    修改密码
    """

    def post(self, request):
        """
        修改用户密码，首先校验原密码，其次检查原密码与新密码是否一致
        :param request:
        :return:
        """
        if request.data.__contains__('old_password') and request.data.__contains__('new_password'):
            old_password = request.data['old_password']
            new_password = request.data['new_password']
            user = request.user
            if not user.check_password(old_password):
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '原密码输入错误，请重新输入'})
            if old_password == new_password:
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '新密码与旧密码不允许一致'})
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK, data={'status_code': 0, 'error': ''})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '请求参数错误'})


class ChangeMobileView(APIView):
    """
    修改手机号码
    """

    def post(self, request):
        """
        修改用户手机号码，首先校验短信验证码
        :param request:
        :return:
        """
        if request.data.__contains__('mobile') and request.data.__contains__('verification_code'):
            mobile = request.data['mobile']
            verification_code = request.data['verification_code']
            user = request.user
            redis_key = 'VerificationCode_%s' % user.mobile
            con = get_redis_connection("default")
            if mobile == user.mobile:
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '新手机号不能与旧手机号一致'})
            if User.objects.exclude(id=user.id).filter(mobile=mobile):
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '该手机号已存在'})
            if not con.exists(redis_key):
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '验证码已过期'})
            if verification_code != con.get(redis_key).decode('utf-8'):
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '验证码错误'})
            user.mobile = mobile
            user.save()
            return Response(status=status.HTTP_200_OK, data={'status_code': 0, 'error': ''})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '请求参数错误'})


class RetrievePasswordView(APIView):
    """
    重置密码
    """
    permission_classes = [AllowAny]

    def post(self, request):
        if request.data.__contains__('mobile') and request.data.__contains__('new_password') \
                and request.data.__contains__('verification_code'):
            mobile = request.data['mobile']
            new_password = request.data['new_password']
            verification_code = request.data['verification_code']
            redis_key = 'VerificationCode_%s' % mobile
            con = get_redis_connection("default")
            if not con.exists(redis_key):
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '验证码已过期'})
            value = con.get(redis_key)
            if value.decode('utf-8') != verification_code:
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '验证码错误'})
            try:
                user = User.objects.get(mobile=mobile)
                user.set_password(new_password)
                user.save()
            except User.DoesNotExist:
                return Response(status=status.HTTP_200_OK, data={'status_code': 1, 'error': '该用户不存在'})
            return Response(status=status.HTTP_200_OK, data={'status_code': 0, 'error': ''})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '请求参数错误'})


class UserDetailViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    用户详情视图类
    """
    pagination_class = None

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.action == "update":
            return UserDetailUpdateSerializer
        return UserDetailRetrieveSerializer


class LoginLocationViewSet(APIView):
    """
    登陆位置
    """

    def post(self, request):
        if request.data.__contains__('longitude') and request.data.__contains__('latitude'):
            login_location = Location.objects.filter(user=request.user)
            if login_location:
                Location.objects.filter(user=request.user).update(longitude=request.data['longitude'],
                                                                  latitude=request.data['latitude'])
            else:
                Location.objects.create(user=request.user, longitude=request.data['longitude'],
                                        latitude=request.data['latitude'])
            return Response(status=status.HTTP_200_OK, data={'status_code': 0, 'error': ''})
        return Response(status=status.HTTP_400_BAD_REQUEST, data={'error': '请求参数错误'})

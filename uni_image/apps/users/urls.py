from django.conf.urls import url
from .views import SmsCodeViewset, RegisterView, ChangeMobileView, ChangePasswordView, RetrievePasswordView, \
    UserDetailViewSet, LoginLocationViewSet

from rest_framework.routers import DefaultRouter

urlpatterns = [
    url(r'^sms_code/', SmsCodeViewset.as_view()),
    url(r'^register/', RegisterView.as_view()),
    url(r'^change_mobile/', ChangeMobileView.as_view()),
    url(r'^change_password/', ChangePasswordView.as_view()),
    url(r'^retrieve_password/', RetrievePasswordView.as_view()),
    url(r'^login_location/', LoginLocationViewSet.as_view()),
]

router = DefaultRouter()
router.register(r'user_detail', UserDetailViewSet, base_name='user_detail')

urlpatterns += router.urls

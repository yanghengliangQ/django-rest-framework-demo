from django.utils.deprecation import MiddlewareMixin


class ResponseDataMiddleware(MiddlewareMixin):
    """
    自定义中间件
    """

    def process_request(self, request):
        pass

    def process_response(self, request, response):
        pass

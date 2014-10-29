import bernhard
import time

from django.conf import settings
from django.core.exceptions import MiddlewareNotUsed


class TimingMiddleware():

    def __init__(self):
        if settings.RIEMANN_ENABLED:
            self.client = bernhard.Client(host=settings.RIEMANN_HOST, transport=bernhard.UDPTransport)
        else:
            raise MiddlewareNotUsed

    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            delta = time.time() - request.start_time
            self.client.send({
                'host': 'django',
                'service': 'sitegen',
                'metric': delta,
                'tags' : ['timing'],
            })
        return response
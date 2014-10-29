import bernhard
import traceback

from django.conf import settings


class ExceptionMiddleware():

    def __init__(self):

        if not hasattr(settings, 'RIEMANN_ENABLED'):
            raise AssertionError, 'Please declare RIEMANN_ENABLED in settings.py'

        if settings.RIEMANN_ENABLED:
            self.client = bernhard.Client(host=settings.RIEMANN_HOST, transport=bernhard.UDPTransport)

    def process_exception(self, request, exception):

        if settings.RIEMANN_ENABLED:
            self.client.send({
                'host': request.META['HTTP_HOST'],
                'service' : 'sitegen',
                'description' : traceback.format_exc(),
                'tags' : ['exception', 'ExceptionMiddleware'],
            })

        return None
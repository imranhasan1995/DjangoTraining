import logging

logger = logging.getLogger('django')
class LoggingMixin:
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"{request.method} request made to {request.path}")
        return super().dispatch(request, *args, **kwargs)
import logging

logger = logging.getLogger("django.request")


class RequestDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        logger.error(
            "REQUEST DEBUG | "
            "scheme=%s | "
            "host=%s | "
            "HTTP_HOST=%s | "
            "X_FORWARDED_PROTO=%s | "
            "X_FORWARDED_HOST=%s | "
            "X_FORWARDED_PORT=%s | "
            "REMOTE_ADDR=%s | "
            "PATH=%s",
            request.scheme,
            request.get_host(),
            request.META.get("HTTP_HOST"),
            request.META.get("HTTP_X_FORWARDED_PROTO"),
            request.META.get("HTTP_X_FORWARDED_HOST"),
            request.META.get("HTTP_X_FORWARDED_PORT"),
            request.META.get("REMOTE_ADDR"),
            request.path,
        )

        try:
            response = self.get_response(request)
            logger.error(
                "REQUEST DEBUG | response_status=%s",
                response.status_code,
            )
            return response
        except Exception:
            logger.exception("REQUEST DEBUG | EXCEPTION")
            raise
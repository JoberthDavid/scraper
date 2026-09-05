import traceback


class RequestDebugMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(
            "REQUEST DEBUG | "
            f"scheme={request.scheme} | "
            f"host={request.get_host()} | "
            f"HTTP_HOST={request.META.get('HTTP_HOST')} | "
            f"X_FORWARDED_PROTO={request.META.get('HTTP_X_FORWARDED_PROTO')} | "
            f"X_FORWARDED_HOST={request.META.get('HTTP_X_FORWARDED_HOST')} | "
            f"X_FORWARDED_PORT={request.META.get('HTTP_X_FORWARDED_PORT')} | "
            f"REMOTE_ADDR={request.META.get('REMOTE_ADDR')} | "
            f"PATH={request.path}",
            flush=True,
        )

        try:
            response = self.get_response(request)

            print(
                f"REQUEST DEBUG | response_status={response.status_code}",
                flush=True,
            )

            if response.status_code >= 500:
                print(
                    f"REQUEST DEBUG | response_class={response.__class__.__name__}",
                    flush=True,
                )
                print(
                    f"REQUEST DEBUG | content_type={response.get('Content-Type')}",
                    flush=True,
                )
                print(
                    f"REQUEST DEBUG | response_body={response.content[:5000]!r}",
                    flush=True,
                )

            return response

        except Exception:
            print("REQUEST DEBUG | EXCEPTION", flush=True)
            traceback.print_exc()
            raise
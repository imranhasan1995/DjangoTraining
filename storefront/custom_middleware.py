class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response  # required

    def __call__(self, request):
        # Log request details
        print(f"Request Method: {request.method}, Request Path: {request.path}")

        # Call the next middleware or view
        response = self.get_response(request)

        # (Optional) Log response details
        print(f"Response status: {response.status_code}")

        return response

class NoCacheMiddleware:
    """
    Prevents LiteSpeed and browsers from caching dashboard responses.
    Without this, LiteSpeed serves stale HTML for minutes after deploys.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Skip static/media files — WhiteNoise handles those with correct headers
        path = request.path_info
        if path.startswith('/static/') or path.startswith('/media/'):
            return response
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        # LiteSpeed-specific: tells LSCache not to store this response
        response['X-LiteSpeed-Cache-Control'] = 'no-cache'
        return response

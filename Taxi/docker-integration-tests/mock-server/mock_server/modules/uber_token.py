from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/oauth/v2/token', self.handle_oauth_v2_token)

    @staticmethod
    def handle_oauth_v2_token(request):
        return web.json_response({
            'access_token': 'some_token',
            'token_type': 'Bearer',
            'expires_in': 2592000,
            'scope': 'business.receipts',
        })

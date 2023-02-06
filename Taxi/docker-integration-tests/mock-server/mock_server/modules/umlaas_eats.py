from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/umlaas-eats/v1/eta', handler_umlaas_eta,
        )


async def handler_umlaas_eta(_):
    return web.json_response(
        {
            'code': 'DEFAULT_MOCK',
            'message': 'this is fatal error from default mock',
        },
        status=500,
    )

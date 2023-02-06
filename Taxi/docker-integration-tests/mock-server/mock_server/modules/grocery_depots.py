from aiohttp import web


async def internal_v1_depots_v1_depots(_):
    return web.json_response({'depots': [], 'errors': []})


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/internal/v1/depots/v1/depots',
            internal_v1_depots_v1_depots,
        )

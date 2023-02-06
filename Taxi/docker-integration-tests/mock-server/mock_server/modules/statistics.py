from aiohttp import web


async def get_fallbacks(_):
    return web.json_response({'fallbacks': []})


async def get_quotas(_):
    return web.json_response(
        {
            'quotas': [
                {
                    'resource': 'py2-do-processing-iteration',
                    'assigned-quota': 1000,
                },
            ],
        },
    )


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/v1/service/health', get_fallbacks)
        self.router.add_get('/v1/rps-quotas', get_quotas)

import logging

from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v2/match', match)


async def match(request):
    logging.info(await request.text())
    return web.json_response(
        {
            'entities': [
                {
                    'id': 'dbid_uuid_0',
                    'tags': ['yandex', 'manager'],
                },
            ],
        },
    )

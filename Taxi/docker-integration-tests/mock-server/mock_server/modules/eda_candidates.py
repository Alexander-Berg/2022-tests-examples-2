from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/list-by-ids', list_by_ids_handler)


async def list_by_ids_handler(request):
    return web.json_response(
        {
            'candidates': [
                {
                    'id': 'test',
                    'position': [
                        55.766491,
                        37.622333,
                    ],
                },
                {
                    'id': 'test1',
                    'position': [
                        55.766491,
                        37.622333,
                    ],
                },
            ],
        },
    )

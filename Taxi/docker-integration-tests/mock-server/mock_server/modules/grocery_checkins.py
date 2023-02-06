from aiohttp import web


async def grocery_shifts_depots(_):
    return web.json_response({'depot_ids': ['1']})


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get(
            '/internal/checkins/v1/grocery-shifts/depots',
            grocery_shifts_depots,
        )

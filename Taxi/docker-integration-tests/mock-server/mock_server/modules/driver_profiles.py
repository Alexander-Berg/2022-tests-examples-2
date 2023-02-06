from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get(
            '/v1/eats-couriers-binding/updates', handle_binding_updates,
        )
        self.router.add_post(
            '/v1/driver/profiles/retrieve', handle_driver_profiles,
        )


async def handle_binding_updates(request):
    return web.json_response(
        {'has_next': False, 'last_known_revision': 'revision', 'binding': []},
    )


async def handle_driver_profiles(request):
    return web.json_response(
        {'profiles': [{'data': {'external_ids': {'eats': '3'}}}]},
    )

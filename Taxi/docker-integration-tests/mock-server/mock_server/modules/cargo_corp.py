from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()

        self.router.add_post(
            '/internal/cargo-corp/v1/client/traits', v1_client_traits,
        )


async def v1_client_traits(_):
    return web.json_response({'is_small_business': True})

from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/v1/blocks', self.handle_v1_blocks)
        self.router.add_get(
            '/v1/blocks/updates', self.handle_v1_blocks_updates,
        )
        self.router.add_post(
            '/v1/blocks/updates', self.handle_v1_blocks_updates,
        )

    @staticmethod
    def handle_v1_blocks_updates(request):
        return web.json_response(
            headers={'X-Polling-Delay-Ms': '0'}, data={'entities': []},
        )

    @staticmethod
    async def handle_v1_blocks(request):
        data = await request.json()
        return web.json_response(
            dict(
                entities_by_id=[
                    dict(entity_id=x, entities=[dict(data={})])
                    for x in data['entity_id_in_set']
                ],
            ),
        )

from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/', self.post_saturn)

    async def post_saturn(self, _):
        return web.json_response(
            {
                'reqid': 'fff-785647',
                'puid': 76874335,
                'score': 0.88,
                'score_raw': 90,
                'formula_id': '785833',
                'formula_description': 'bnpl_market',
                'data_source': 'puid/2021-06-21',
                'status': 'ok',
            },
        )

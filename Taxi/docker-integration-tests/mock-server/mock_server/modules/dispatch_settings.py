from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/v1/categories/fetch', self.v1_categories_fetch)
        self.router.add_get('/v1/settings/fetch', self.v1_settings_fetch)
        self.router.add_get('/v2/categories/fetch', self.v2_categories_fetch)
        self.router.add_post('/v2/settings/fetch', self.v2_settings_fetch)

    @staticmethod
    def v1_categories_fetch(request):
        return web.json_response(
            {
                'settings': [
                    {
                        'type': 'common_dispatch',
                        'categories': [
                            {
                                'zone_name': '__default__',
                                'tariff_names': ['__default__'],
                            },
                        ],
                    },
                ],
            },
        )

    @staticmethod
    def v1_settings_fetch(request):
        return web.json_response({'settings': []})

    @staticmethod
    def v2_categories_fetch(request):
        return web.json_response(
            {
                'categories': [
                    {
                        'zone_name': '__default__',
                        'tariff_names': ['__default__'],
                    },
                ],
                'groups': [
                    {
                        'group_name': '__default__',
                        'tariff_names': ['__default__'],
                    },
                ],
            },
        )

    @staticmethod
    def v2_settings_fetch(request):
        return web.json_response({'settings': []})

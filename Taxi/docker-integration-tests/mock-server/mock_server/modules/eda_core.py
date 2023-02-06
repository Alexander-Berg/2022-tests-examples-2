from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/server/api/v1/supply/pickers-list', self.handle_pickers_list,
        )
        self.router.add_post(
            '/server/api/v1/surge/logistic-groups',
            self.handle_surge_logistic_groups,
        )
        self.router.add_post(
            '/server/api/v1/surge/courier-activity',
            self.handle_surge_courier_activity,
        )
        self.router.add_post(
            '/server/api/v1/surge/supply', self.handle_surge_supply,
        )
        self.router.add_get(
            '/server/api/v1/export/settings/surge-regions',
            self.handle_surge_regions,
        )
        self.router.add_post(
            '/server/api/v1/surge/logistic-groups',
            self.handle_surge_log_groups,
        )

    def handle_pickers_list(self, request):
        return web.json_response(
            {
                'payload': {
                    'pickers': [
                        {
                            'id': 1,
                            'phone_id': '1',
                            'name': 'Test1',
                            'available_until': '2100-10-08T14:00:00+0300',
                            'available_places': [305693],
                            'requisite_type': 'TinkoffCard',
                            'requisite_value': '1234567890',
                        },
                        {
                            'id': 2,
                            'phone_id': '2',
                            'name': 'Сидоров Пётр Петрович',
                            'available_until': '2100-10-08T14:00:00+0300',
                            'available_places': [305694],
                            'requisite_type': 'TinkoffCard',
                            'requisite_value': '0987654321',
                        },
                    ],
                },
            },
        )

    def handle_surge_logistic_groups(self, request):
        return web.json_response({'payload': [], 'meta': {'count': 0}})

    def handle_surge_courier_activity(self, request):
        return web.json_response({'payload': [], 'meta': {'count': 0}})

    def handle_surge_supply(self, request):
        return web.json_response({'payload': [], 'meta': {'count': 0}})

    def handle_surge_regions(self, request):
        return web.json_response({'payload': []})

    def handle_surge_log_groups(self, request):
        return web.json_response({'payload': []})

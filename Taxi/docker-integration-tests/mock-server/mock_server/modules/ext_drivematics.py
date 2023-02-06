from aiohttp import web

class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get('/v1/parks/car/list', self.handle_list_request)

    async def handle_list_request(self, request):
        return web.json_response(
            {
                'tags_array': [
                    {
                        'name': 'leasing_has_telematics_tag',
                        'cars_count_zero': 1,
                        'description': {
                            'name': 'leasing_has_telematics_tag',
                            'index': 11,
                            'comment': 'base object',
                            'display_name': 'leasing_has_telematics_tag',
                        },
                        'cars_count': 222,
                        'cars_count_prior': 0,
                    },
                    {
                        'name': 'brand_tag_test',
                        'cars_count_zero': 213,
                        'description': {
                            'name': 'brand_tag_test',
                            'index': 1111,
                            'tag_flow_priority': 0,
                            'taxi_companies_tins': ['111111111111'],
                            'tag_flow': '',
                            'display_name': 'Тег для бренда 000 Берёзка',
                            'id': '12387138f',
                        },
                        'cars_count': 213,
                        'cars_count_prior': 0,
                    },
                ],
                'cars': [
                    {
                        'number': 'NUMBER',
                        'imei': 'IMEI',
                        'vin': 'XXX',
                        'tags': [
                            {
                                'tag_id': 'ID',
                                'priority': 0,
                                'tag': 'brand_tag_test',
                                'display_name': 'Тег для бренда ООО Берёзка',
                                'object_id': 'OBJECT_ID',
                            },
                        ],
                    },
                ],
                'can_get_more_pages': False,
                'page_size': 1000,
            },
        )

from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post('/user_phones/get', self.handler_user_phones_get)

    async def handler_user_phones_get(self, _):
        return web.json_response(
            {
                'created': '2019-02-01T13:00:00+0000',
                'id': '539e99e1e7e5b1f5398adc5b',
                'is_loyal': False,
                'is_taxi_staff': False,
                'is_yandex_staff': False,
                'last_freecancel': '2019-02-01T13:30:00+0000',
                'last_payment_method': {'id': '1', 'type': 'card'},
                'personal_phone_id': '507f191e810c19729de860ea',
                'phone': '+79991234569',
                'phone_hash': '123',
                'phone_salt': '132',
                'stat': {
                    'big_first_discounts': 1,
                    'complete': 15,
                    'complete_apple': 6,
                    'complete_card': 1,
                    'complete_google': 5,
                    'fake': 1,
                    'total': 100,
                },
                'type': 'yandex',
                'updated': '2019-02-01T13:00:00+0000',
            },
        )

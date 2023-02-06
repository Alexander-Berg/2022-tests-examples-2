from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_post(
            '/v1/calculate-discount', self.v1_calculate_discount,
        )
        self.router.add_post('/v1/peek-discount', self.v1_peek_discount)
        self.router.add_post(
            '/v1/check-discount-restrictions',
            self.v1_check_discount_restrictions,
        )
        self.router.add_post(
            '/v1/branding-settings-by-zone', self.v1_branding_settings_by_zone,
        )
        self.router.add_post('/v1/get-discount', self.v1_get_discount)
        self.router.add_post('/v1/acquire-discount', self.v1_acquire_discount)
        self.router.add_post('/v1/release-discount', self.v1_release_discount)
        self.router.add_post('/v2/get-discount', self.v2_get_discount)
        self.router.add_post('/v3/get-discount', self.v3_get_discount)

    @staticmethod
    def v1_calculate_discount(request):
        return web.json_response(
            {'discount_offer_id': '012345678901234567890123', 'discounts': []},
        )

    @staticmethod
    def v1_peek_discount(request):
        return web.json_response({'discounts': []})

    @staticmethod
    def v1_check_discount_restrictions(request):
        return web.json_response({'valid': True})

    @staticmethod
    def v1_branding_settings_by_zone(request):
        return web.json_response({'branding_items': []})

    @staticmethod
    def v1_get_discount(request):
        return web.json_response(
            {'discount_offer_id': '012345678901234567890123', 'discounts': []},
        )

    @staticmethod
    def v1_acquire_discount(request):
        return web.json_response({'result': True})

    @staticmethod
    def v1_release_discount(request):
        return web.json_response({'result': True})

    @staticmethod
    def v2_get_discount(request):
        return web.json_response({})

    @staticmethod
    def v3_get_discount(request):
        return web.json_response(
            {'discount_offer_id': '012345678901234567890123', 'discounts': {}},
        )

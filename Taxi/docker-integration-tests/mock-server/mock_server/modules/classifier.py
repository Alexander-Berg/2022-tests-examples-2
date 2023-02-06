from aiohttp import web


class Application(web.Application):
    def __init__(self):
        super().__init__()
        self.router.add_get(
            '/v1/classifiers/updates', self.v1_classifiers_updates,
        )
        self.router.add_post(
            '/v1/classification-rules/updates',
            self.v1_classification_rules_updates,
        )
        self.router.add_post(
            '/v1/classifier-tariffs/updates',
            self.v1_classifier_tariffs_updates,
        )
        self.router.add_post(
            '/v1/cars-first-order-date/updates', self.v1_cars_first_order_date,
        )
        self.router.add_post(
            '/v1/classifier-exceptions/updates', self.v1_exceptions_updates,
        )
        self.router.add_post(
            '/v2/classifier-exceptions/updates', self.v2_exceptions_updates,
        )

    @staticmethod
    def v1_classifiers_updates(request):
        return web.json_response({'classifiers': []})

    @staticmethod
    def v1_classification_rules_updates(request):
        return web.json_response({'classification_rules': [], 'limit': 100})

    @staticmethod
    def v1_classifier_tariffs_updates(request):
        return web.json_response({'tariffs': [], 'limit': 100})

    @staticmethod
    def v1_cars_first_order_date(request):
        return web.json_response({'cars_first_order_date': [], 'limit': 100})

    @staticmethod
    def v1_exceptions_updates(request):
        return web.json_response({'classifier_exceptions': [], 'limit': 100})

    @staticmethod
    def v2_exceptions_updates(request):
        return web.json_response(
            {'classifier_exceptions_V2': [], 'limit': 100})

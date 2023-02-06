import pytest

from tests_grocery_cart.plugins import keys


BASIC_OFFER = {
    'result_action': 'created',
    'offer_data': {
        'offer_id': keys.CREATED_OFFER_ID,
        'offer_time': keys.TS_NOW,
        'is_surge': False,
    },
}


# TODO: вынести в grocery-mocks https://st.yandex-team.ru/LAVKABACKEND-4776
@pytest.fixture(name='offers', autouse=True)
def simple_offer_service(mockserver):
    class Context:
        def __init__(self):
            self.offers_created = 0

            # # Some predefined cache
            self.offer_storage = {}

        def add_offer(self, offer_id, params, payload):
            if offer_id not in self.offer_storage.keys():
                self.offer_storage[offer_id] = {
                    'params': params,
                    'payload': payload,
                }

        def add_offer_elementwise(
                self, offer_id, offer_time, depot_id, location,
        ):
            if offer_id not in self.offer_storage.keys():
                self.offer_storage[offer_id] = {
                    'params': {
                        'depot_id': depot_id,
                        'lat_lon': ';'.join([str(item) for item in location]),
                    },
                    'payload': {
                        'request_time': offer_time.astimezone().isoformat(),
                    },
                }

        @property
        def created_times(self):
            return self.offers_created

        @property
        def match_create_times_called(self):
            return _match_create.times_called

    ctx = Context()

    @mockserver.json_handler('/grocery-offers/v1/create')
    def _create(request):
        body = request.json
        ctx.add_offer(str(ctx.offers_created), body['params'], body['payload'])
        ctx.offers_created += 1

        return {'id': str(ctx.offers_created - 1)}

    @mockserver.json_handler(
        '/grocery-offers/internal/v1/offers/v1/match-create',
    )
    def _match_create(request):
        offer_id = None
        if request.json['current_id']:
            offer_id = request.json['current_id']

        # ищем по id
        if offer_id is not None:
            if offer_id in ctx.offer_storage:
                offer = ctx.offer_storage[offer_id]
                return {
                    'id': offer_id,
                    'matched': True,
                    'offer_params': offer['params'],
                    'payload': offer['payload'],
                }

        # ищем по параметрам
        params = request.json['params']
        for offer_id, offer in ctx.offer_storage.items():
            if offer['params'] == params:
                return {
                    'id': offer_id,
                    'matched': True,
                    'offer_params': offer['params'],
                    'payload': offer['payload'],
                }

        # не нашли — значит, надо создать
        new_id = str(ctx.offers_created)
        ctx.add_offer(new_id, request.json['params'], request.json['payload'])
        ctx.offers_created += 1

        return {
            'id': new_id,
            'matched': False,
            'not_matched_reason': 'OFFER_NOT_FOUND',
            'offer_params': request.json['params'],
            'payload': request.json['payload'],
        }

    return ctx

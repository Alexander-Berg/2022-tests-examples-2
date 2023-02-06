import pytest
# root conftest for service grocery-market-gw
pytest_plugins = ['grocery_market_gw_plugins.pytest_plugins']


# copy-paste from g-api
@pytest.fixture(name='offers', autouse=True)
def simple_offer_service(mockserver):
    class Context:
        def __init__(self):
            self.offers_created = 0

            # Some predefined cache
            self.offer_storage = {}
            for i in range(5):
                # Warning: time should be rounded
                self.add_offer(
                    str(i),
                    {
                        'place_id': str(110 + i),
                        'offer_time': '2020-02-20T10:05:00+00:00',
                    },
                    {'surge_info': {'load_level': i}},
                )

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
        def matched_times(self):
            return match.times_called

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

    @mockserver.json_handler('/grocery-offers/v1/create/multi')
    def _create_multi(request):
        offers = request.json['offers']
        ans = []
        index = ctx.offers_created
        for offer in offers:
            ctx.add_offer(
                str(len(ctx.offer_storage)), offer['params'], offer['payload'],
            )
            ans.append(str(index))
            index += 1

        ctx.offers_created += len(offers)
        return {'ids': ans}

    @mockserver.json_handler('/grocery-offers/v1/match/multi')
    def match(request):
        body_offers = request.json['offers']
        ans = []
        for offer_id in ctx.offer_storage:
            offer = ctx.offer_storage[offer_id]
            for body in body_offers:
                if offer['params'] == body['params']:
                    result = {
                        'matched': True,
                        'offer_params': offer['params'],
                        'payload': offer['payload'],
                    }
                    ans.append(result)
        return {'offers': ans}

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
            'offer_params': request.json['params'],
            'payload': request.json['payload'],
        }

    # pylint: disable=unused-variable
    @mockserver.json_handler('/eda-surge-calculator/v1/calc-surge-grocery')
    def calc(request):
        results = []
        for place_id in request.json['place_ids']:
            lvl = 0
            if 100 <= place_id < 200:
                lvl = place_id % 10
            else:
                continue
            item = {
                'calculator_name': 'calc_surge_grocery_v1',
                'results': [
                    {
                        'place_id': place_id,
                        'result': {'load_level': lvl, 'delivery_zone_id': 55},
                    },
                ],
            }
            results.append(item)

        return {'results': results, 'errors': []}

    @mockserver.json_handler('/grocery-offers/v1/retrieve/by-id')
    def retrieve(request):
        offer_id = request.json['id']
        offer = {}
        if offer_id in ctx.offer_storage.keys():
            offer = ctx.offer_storage[offer_id]
            offer['id'] = offer_id
            offer['tag'] = 'offer_tag'
            offer['payload']['request_time'] = offer['params']['offer_time']
            offer['due'] = '2022-02-20T10:05:00+00:00'
        return offer

    return ctx

import pytest


class Key:
    def __init__(self, service_id, eats_and_lavka_id):
        self._service_id = service_id
        self._eats_and_lavka_id = eats_and_lavka_id

    def __hash__(self):
        return hash((self._service_id, self._eats_and_lavka_id))

    def __eq__(self, other):
        if isinstance(other, Key):
            return (
                self._service_id == other.service_id
                and self._eats_and_lavka_id == other.eats_and_lavka_id
            )
        return NotImplemented

    @property
    def service_id(self):
        return self._service_id

    @property
    def eats_and_lavka_id(self):
        return self._eats_and_lavka_id


class Response:
    def __init__(self, market_feed_id, partner_id, business_id):
        self._market_feed_id = market_feed_id
        self._partner_id = partner_id
        self._business_id = business_id

    @property
    def market_feed_id(self):
        return self._market_feed_id

    @property
    def partner_id(self):
        return self._partner_id

    @property
    def business_id(self):
        return self._business_id


@pytest.fixture(name='mbi_api', autouse=True)
def mock_mbi_api(mockserver):
    class Context:
        def __init__(self):
            self._depots = {}

        def add_depot(
                self,
                service_id,
                eats_and_lavka_id,
                market_feed_id,
                partner_id,
                business_id,
        ):
            key = Key(service_id, eats_and_lavka_id)
            response = Response(market_feed_id, partner_id, business_id)
            self._depots[key] = response

        def get_response(self, service_id, eats_and_lavka_id):
            key = Key(service_id, eats_and_lavka_id)
            return self._depots.get(key)

        @property
        def depots(self):
            return self._depots

        @property
        def times_called(self):
            return mock_market_credentials_handler.times_called

    @mockserver.json_handler(
        '/mbi-api/eats-and-lavka/get-or-create/market-credentials',
    )
    def mock_market_credentials_handler(request):
        assert request.json['service_id'] is not None
        assert request.json['eats_and_lavka_id'] is not None
        assert request.json['uid'] == 1410293377
        response = context.get_response(
            request.json['service_id'], request.json['eats_and_lavka_id'],
        )
        if response is None:
            return {}
        return {
            'market_feed_id': response.market_feed_id,
            'partner_id': response.partner_id,
            'business_id': response.business_id,
        }

    context = Context()
    return context

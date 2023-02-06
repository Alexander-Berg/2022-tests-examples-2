NAME = 'fleet-offers'


def _handler_internal_v1_fleet_offers_v1_offers_by_kind(context):
    def handler(request):
        assert request.query['park_id'] == '48b7b5d81559460fb1766938f94009c1'
        assert request.query['driver_id'] == '48b7b5d81559460fb176693800000001'
        return {
            'id': '00000000-0001-0001-0000-000000000000',
            'rev': 0,
            'name': 'a',
            'number': 12345,
            'kind': 'offer',
            'signed_at': '2021-01-01T00:00:00.000000000+00:00',
        }

    return handler


def setup(context, mockserver):
    mocks = {}

    def add(url, handler):
        mocks[url] = mockserver.json_handler('/' + NAME + url)(handler)

    add(
        '/internal/v1/fleet-offers/v1/offers/by-kind',
        _handler_internal_v1_fleet_offers_v1_offers_by_kind(context),
    )

    return mocks

# pylint: disable=redefined-outer-name

import pytest


@pytest.fixture
def basic_mocks(mockserver, logistic_platform_dir):
    async def wrapper(*, employer_names=None, order_sources=None, polygon=None):
        @mockserver.json_handler('/typed-geoareas/v1/fetch_geoareas')
        def geoareas(request):
            return {
                'geoareas': [],
                'removed': [],
            }

        @mockserver.json_handler('/monitoring/push')
        def monitoring_push(request):
            print(request)
            return {}

        @mockserver.handler('/search/stable/yandsearch')
        def geocoder(request):
            path = logistic_platform_dir.joinpath('dispatcher/ut_platform/resources/geocoder/geo_ans')
            in_file = open(path, 'rb')
            data = in_file.read()
            in_file.close()
            return mockserver.make_response(
            response=data,
            status=200,
        )

        @mockserver.json_handler('/v1/next-day-delivery/client/calc-offer-price')
        def calc_offer_price(request):
            return {}

    return wrapper

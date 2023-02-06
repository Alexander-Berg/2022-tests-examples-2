import pytest


USER_ID = 1
PERSONAL_PHONE_ID = 2
OFFER_ID = 1
ORDER_ID = '1'


@pytest.fixture(autouse=True)
def geocoder_mock(mockserver):
    @mockserver.json_handler('/geocoder/yandsearch')
    async def handler(request):
        return {
            'features': [
                {
                    'properties': {
                        'GeocoderMetaData': {
                            'Address': {
                                'Components': [],
                                'formatted': 'Moscow',
                            },
                        },
                    },
                },
            ],
        }

    return handler


@pytest.fixture(autouse=True)
def int_profile_mock(mockserver):
    @mockserver.json_handler('/yandex-int-api/v1/profile')
    async def handler(request):
        return {'user_id': USER_ID, 'personal_phone_id': PERSONAL_PHONE_ID}

    return handler


@pytest.fixture(autouse=True)
def int_estimate_mock(mockserver):
    @mockserver.json_handler('/yandex-int-api/v1/orders/estimate')
    async def handler(request):
        return {'offer': OFFER_ID}

    return handler


@pytest.fixture(autouse=True)
def order_satisfy_mock(mockserver):
    @mockserver.json_handler('/candidates/order-satisfy')
    async def handler(request):
        return {'candidates': [{'is_satisfied': True}]}

    return handler


@pytest.fixture(autouse=True)
def int_order_draft_mock(mockserver):
    @mockserver.json_handler('/yandex-int-api/v1/orders/draft')
    async def handler(request):
        return {'orderid': ORDER_ID}

    return handler


@pytest.fixture(autouse=True)
def int_order_commit_mock(mockserver):
    @mockserver.json_handler('/yandex-int-api/v1/orders/commit')
    async def handler(request):
        return {'orderid': ORDER_ID, 'status': 'search'}

    return handler

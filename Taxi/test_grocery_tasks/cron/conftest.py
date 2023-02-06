import pytest


@pytest.fixture
def mock_geobase(mockserver):
    def mocker(path, prefix=False, raw_request=False):
        def wrapper(func):
            full_path = '/geobase' + path
            return mockserver.json_handler(
                full_path, prefix=prefix, raw_request=raw_request,
            )(func)

        return wrapper

    mocker.make_response = mockserver.make_response
    return mocker


@pytest.fixture  # noqa: F405
def geobase(mockserver, load_json):
    def _wrapper():
        @mockserver.json_handler('/geobase/v1/region_by_id')
        async def region_by_id(request):  # pylint: disable=unused-variable
            data = load_json('geobase_response.json')
            return data

        return region_by_id

    return _wrapper


@pytest.fixture
def mbi_api(mockserver, load_json):
    @mockserver.json_handler(
        '/mbi-api/eats-and-lavka/get-or-create/market-credentials',
    )
    def _mock_mbi_api(request):
        response_json = load_json('mbi_api_response_depots.json')
        return response_json[request.json['service_id']][
            request.json['eats_and_lavka_id']
        ]

    return _mock_mbi_api


@pytest.fixture(name='grocery_menu', autouse=True)
def grocery_menu(mockserver, load_json):
    is_return_data = False

    @mockserver.json_handler(
        '/grocery-menu/internal/v1/menu/v1/combo-products/list',
    )
    def _mock_grocery_menu(request):
        if not is_return_data:
            return {'combo_products': [], 'cursor': 0}
        if 'cursor' not in request.json:
            return load_json('grocery_menu_combos_list.json')
        return {'combo_products': [], 'cursor': 1}

    class Context:
        def __init__(self):
            pass

        def set_return_data(self, flag):
            nonlocal is_return_data
            is_return_data = flag

    context = Context()

    return context

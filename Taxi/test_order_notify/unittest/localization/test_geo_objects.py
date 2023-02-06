import pytest

from order_notify.generated.stq3 import stq_context
from order_notify.repositories.localization import geo_objects
from order_notify.repositories.route.route_info import RouteData


DEFAULT_ROUTE_DATA = RouteData(
    source={'short_text': 'short', 'geopoint': [4.2, 2.5]},
    destinations=[{'short_text': 'dst', 'geopoint': [4.2, 2.5]}],
    final_destination=None,
    track_points=[[2.2, 3.3]],
)


TRANSLATE_SHORT_TEXT = {
    'short': 'шорт',
    'dst': 'дст',
    'text': 'текст',
    'address': 'адрес',
}


DEFAULT_RESPONSE: dict = {
    'country': 'rus',
    'fullname': 'full',
    'geopoint': [4.2, 2.5],
    'locality': 'ru',
}


@pytest.fixture(name='mock_server')
def mock_server_fixture(mockserver):
    @mockserver.json_handler('/protocol/3.0/localizeaddress')
    async def handler(request):
        assert request.json['locale'] == 'ru'
        request_addresses = request.json['addresses']

        return {
            'addresses': [
                {
                    **DEFAULT_RESPONSE,
                    'short_text': TRANSLATE_SHORT_TEXT[addrss['text']],
                }
                for addrss in request_addresses
            ],
        }

    return handler


@pytest.mark.parametrize(
    'destinations, final_destination, '
    'expected_destinations, expected_final_destination',
    [
        pytest.param([], None, [], None, id='no_destinations_no_finish_point'),
        pytest.param(
            [],
            {'geopoint': [37.534, 55.750], 'short_text': 'dst'},
            [],
            {'short_text': TRANSLATE_SHORT_TEXT['dst'], **DEFAULT_RESPONSE},
            id='no_destinations_exist_finish_point',
        ),
        pytest.param(
            [{'geopoint': [57.534, 15.750], 'short_text': 'text'}],
            {'geopoint': [45.758991, 28.597506], 'short_text': 'address'},
            [{'short_text': TRANSLATE_SHORT_TEXT['text'], **DEFAULT_RESPONSE}],
            {
                'short_text': TRANSLATE_SHORT_TEXT['address'],
                **DEFAULT_RESPONSE,
            },
            id='one_destination_exist_finish_point',
        ),
    ],
)
async def test_localize_route_data(
        stq3_context: stq_context.Context,
        mock_server,
        destinations,
        final_destination,
        expected_destinations,
        expected_final_destination,
):
    expected_route_data = RouteData(
        source={**DEFAULT_RESPONSE, 'short_text': 'шорт'},
        destinations=expected_destinations,
        final_destination=expected_final_destination,
        track_points=[[2.2, 3.3]],
    )
    route_data = await geo_objects.localize_route_data(
        context=stq3_context,
        route_data=RouteData(
            source={'short_text': 'short', 'geopoint': [4.2, 2.5]},
            destinations=destinations,
            final_destination=final_destination,
            track_points=[[2.2, 3.3]],
        ),
        locale='ru',
    )
    assert route_data == expected_route_data

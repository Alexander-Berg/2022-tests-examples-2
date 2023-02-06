import json
from typing import Optional
from typing import Set

import pytest

import utils


PA_HEADERS = {
    'X-YaTaxi-UserId': 'user_id',
    'X-YaTaxi-Pass-Flags': 'portal',
    'X-Yandex-UID': '4003514353',
    'X-Ya-User-Ticket': 'user_ticket',
    'X-YaTaxi-PhoneId': '5714f45e98956f06baaae3d4',
    'X-Request-Language': 'ru',
    'X-Request-Application': 'app_name=iphone',
    'X-AppMetrica-DeviceId': 'DeviceId',
}


@pytest.fixture(name='mock_tariffs_promotions')
async def _mock_tariffs_promotions(mockserver, testpoint):
    @mockserver.json_handler('/tariffs-promotions/v1/offer-data')
    def post_order_data(request):
        assert request.method == 'POST'
        offers = request.json['offers']
        assert offers == [
            {
                'offer_id': 'some_offer_id',
                'data': {
                    'route_info': {
                        'points': [],
                        'distance': '9400',
                        'time': '960',
                    },
                    'currency': 'RUB',
                    'categories': [
                        {
                            'name': 'econom',
                            'estimated_seconds': 180,
                            'final_price': '1405',
                            'driver_funded_discount_value': '3',
                        },
                    ],
                },
            },
        ]

        return {}

    @testpoint('post_offer_data')
    def data_posted(data):
        pass

    yield None

    await data_posted.wait_call()
    assert post_order_data.times_called == 1


# Use two files to catch race conditions:
# to do it we need to serve /routestats at least twice.
@pytest.mark.parametrize(
    'resp_file, backend, uri',
    [
        ('protocol_response.json', 'protocol-routestats', 'v1/routestats'),
        ('protocol_response_2.json', 'protocol-routestats', 'v1/routestats'),
        ('protocol_response.json', 'integration-api', 'int-api/v1/routestats'),
    ],
)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'top_level:tariffs-promotions-hook',
        'brandings:proxy',
    ],
)
async def test_basic_protocol_proxying(
        resp_file,
        backend,
        uri,
        taxi_routestats,
        mockserver,
        load_json,
        mock_tariffs_promotions,
):
    class Context:
        req = None

    protocol_context = Context()

    @mockserver.json_handler(f'/{backend}/internal/routestats')
    def _protocol(request):
        protocol_context.req = request.json
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json(resp_file),
        }

    req = load_json('request.json')
    response = await taxi_routestats.post(uri, req)
    assert response.status_code == 200

    expected_response = load_json(resp_file)
    assert expected_response == response.json()

    utils.sort_requests_for_comparison(req, protocol_context.req)
    assert req == protocol_context.req


# We expect only 400, 401, 404, 429, 500 codes from /internal/routestats.
@pytest.mark.parametrize(
    'code,exp_code',
    [(400, 400), (401, 401), (404, 404), (500, 500), (429, 429)],
)
@pytest.mark.parametrize(
    'backend, uri',
    [
        ('protocol-routestats', 'v1/routestats'),
        ('integration-api', 'int-api/v1/routestats'),
    ],
)
@pytest.mark.routestats_plugins(names=['top_level:proxy'])
async def test_protocol_error_transparently_proxied(
        taxi_routestats, mockserver, load_json, code, exp_code, backend, uri,
):
    error_resp = {}

    @mockserver.handler(f'/{backend}/internal/routestats')
    def _protocol(request):
        return mockserver.make_response(json.dumps(error_resp), code)

    req = load_json('request.json')
    response = await taxi_routestats.post(uri, req)
    assert response.status_code == exp_code
    assert response.json() == error_resp


@pytest.mark.parametrize(
    'backend, uri',
    [
        ('protocol-routestats', 'v1/routestats'),
        ('integration-api', 'int-api/v1/routestats'),
    ],
)
@pytest.mark.routestats_plugins(names=['top_level:proxy'])
async def test_protocol_headers_transparently_proxied(
        taxi_routestats, mockserver, load_json, backend, uri,
):
    req_headers = {
        'User-Agent': 'ua',
        'Accept-Language': 'ru-RU',
        'X-Remote-IP': '127.0.0.1',
        'X-Requested-With': 'nodejs',
        'X-Requested-Uri': '/some/uri',
        'X-Taxi': 'taxi-frontend',
        'Authorization': 'Bearer 123',
        'Cookie': 'a=b; c=d',
        'Origin': 'https://somesite.com',
    }

    @mockserver.json_handler(f'/{backend}/internal/routestats')
    def _protocol(request):
        for header_name, value in req_headers.items():
            assert [value] == request.headers.getall(header_name)
        return {'internal_data': {}, **load_json('protocol_response.json')}

    req = load_json('request.json')
    response = await taxi_routestats.post(uri, headers=req_headers, json=req)
    assert response.status_code == 200


@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=[
        'top_level:proxy',
        'top_level:brandings',
        'brandings:proxy',
        'top_level:drive_order_flow',
        'top_level:title:title_drive',
    ],
)
@pytest.mark.experiments3(filename='drive_service_level_selector_exp.json')
@pytest.mark.config(
    APPLICATION_BRAND_CATEGORIES_SETS={'__default__': ['drive']},
)
@pytest.mark.translations(
    client_messages={
        'drive.no_service': {'ru': 'Нет машин Драйва'},
        'summary.drive.button.title': {'ru': 'Го на Драйве'},
    },
)
async def test_routestats_with_drive(taxi_routestats, mockserver, load_json):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response_with_drive.json'),
        }

    @mockserver.json_handler('/yandex-drive/offers/fixpoint')
    def _mock_yandex_drive(request):
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket'
        assert request.headers['Lon'] == '37.500000'
        assert request.headers['Lat'] == '55.500000'
        assert 'AC-Taxi-App-Build' not in request.headers
        assert request.headers['IC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        assert request.headers['DeviceId'] == 'DeviceId'
        assert (
            request.headers['X-YaTaxi-UserId'] == PA_HEADERS['X-YaTaxi-UserId']
        )
        assert request.args == {
            'src': '37.587569 55.733393',
            'dst': '37.687569 55.633393',
            'destination_name': 'point_b_title',
            'lang': 'ru',
            'offer_count_limit': '5',
        }
        assert request.json == {
            'payment_methods': [
                {
                    'card': 'card-eeeeeeeeeeeeeeeeeeeeeeeee',
                    'account_id': 'card',
                },
            ],
        }
        return mockserver.make_response(
            json=load_json('response_yandex_drive_fixpoint.json'),
            headers={'X-Req-Id': '123'},
        )

    req = load_json('request_with_drive.json')
    response = await taxi_routestats.post(
        'v1/routestats', req, headers=PA_HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('expected_response_with_drive.json')


@pytest.mark.parametrize(
    'is_crutch_experiment',
    [
        pytest.param(
            True,
            marks=pytest.mark.experiments3(
                filename='routestats_requirements_crutch.json',
            ),
        ),
        pytest.param(False),
    ],
)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=['top_level:proxy', 'top_level:brandings', 'brandings:proxy'],
)
async def test_requirement_crutch(
        taxi_routestats, mockserver, load_json, is_crutch_experiment: bool,
):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        protocol_request = (
            _get_request_with_dtd(
                load_json, categories_with_dtd={'night', 'express', 'courier'},
            )
            if is_crutch_experiment
            else _get_request_with_dtd(load_json)
        )
        input_request = request.json

        utils.sort_requests_for_comparison(input_request, protocol_request)
        assert input_request == protocol_request

        return {
            'internal_data': {'a': 'b'},
            **load_json('protocol_response.json'),
        }

    request = _get_request_with_dtd(load_json)
    response = await taxi_routestats.post('v1/routestats', request)
    assert response.status_code == 200


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='summary_scenarios',
    consumers=['uservices/routestats'],
    clauses=[
        {
            'value': {
                'enabled': True,
                'scenarios': [
                    {
                        'name': 'cheapest',
                        'definitions': [
                            {
                                'name': 'modifier_field',
                                'show_modes': ['selected'],
                                'tanker_key': 'key',
                            },
                        ],
                    },
                ],
            },
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.translations(client_messages={'key': {'ru': 'simple text'}})
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.geoareas(filename='geoareas_moscow.json')
@pytest.mark.routestats_plugins(
    names=['top_level:brandings', 'brandings:summary_scenarios'],
)
async def test_summary_scenarios(taxi_routestats, mockserver, load_json):
    @mockserver.json_handler('/protocol-routestats/internal/routestats')
    def _protocol(request):
        return {
            'internal_data': load_json('internal_data.json'),
            **load_json('protocol_response.json'),
        }

    request = _get_request_with_dtd(load_json)
    response = await taxi_routestats.post('v1/routestats', request)
    assert response.status_code == 200

    service_levels = response.json()['service_levels']
    econom = [x for x in service_levels if x['class'] == 'econom'][0]
    modifier = [
        x for x in econom['brandings'] if x['type'] == 'modifier_field'
    ][0]
    assert modifier == {
        'attributed_info': {
            'attributed_text': {
                'items': [{'text': 'simple text', 'type': 'text'}],
            },
            'show_mode': ['selected'],
        },
        'type': 'modifier_field',
    }


def _get_request_with_dtd(
        load_json, categories_with_dtd: Optional[Set[str]] = None,
) -> dict:
    request = load_json('request.json')
    request['requirements'] = {'door_to_door': True}
    if not categories_with_dtd:
        return request
    for category_requirements in request['tariff_requirements']:
        if category_requirements['class'] in categories_with_dtd:
            category_requirements.setdefault('requirements', {})[
                'door_to_door'
            ] = True
    return request

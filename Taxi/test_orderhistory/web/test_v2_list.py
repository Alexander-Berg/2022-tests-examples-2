import hashlib

# pylint: disable=unused-variable,too-many-lines
from aiohttp import web
import pytest

from taxi.clients import experiments3

from orderhistory.utils import experiments
from orderhistory.views import common


DEFAULT_PHONE_ID = '590c39bcaa7f19871a38ee91'
CORE_EATS_HANDLER_FALLBACK = (
    'handler.eats-orderhistory./internal-api/v1/orders/retrieve-POST.fallback'
)
EATS_ORDERS_INFO_HANDLER_FALLBACK = (
    'handler.eats-orders-info.'
    '/internal/eats-orders-info/v1/retrieve-POST.fallback'
)

DEFAULT_IMAGE_TAGS = {
    '__default__': 'test',
    'first': 'first_image_tag',
    'second': 'second_image_tag',
}


def _default_handle_oh(request, load_json, expected_request, response):
    if isinstance(expected_request, str):
        expected_request = load_json(expected_request)
    assert request.json == expected_request
    return web.json_response(load_json(response))


def _default_handle_ridehistory(
        request, load_json, expected_request, response,
):
    return _default_handle_oh(request, load_json, expected_request, response)


def _default_handle_eats_oh(request, load_json, expected_request, response):
    return _default_handle_oh(request, load_json, expected_request, response)


def _get_handlers_called(service_handler):
    return {
        service
        for service, handler in service_handler.items()
        if handler.times_called > 0
    }


def get_default_headers(phone_id=DEFAULT_PHONE_ID):
    headers = {
        'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
        'Accept-Language': 'ru-RU',
        'X-Yandex-UID': 'uid0',
        'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
        'X-Request-Application': 'app_name=android',
        'X-Request-Language': 'ru',
    }
    if phone_id is not None:
        headers['X-YaTaxi-PhoneId'] = phone_id

    return headers


def get_default_response():
    return {
        'services': {
            'taxi': {
                'image_tags': {'skin_version': '6', 'size_hint': 9999},
                'need_item_view': True,
            },
            'eats': {},
            'grocery': {},
            'shuttle': {},
        },
        'include_service_metadata': True,
    }


@pytest.mark.config(
    ORDERHISTORY_SERVICE_IMAGE_TAGS={
        '__default__': 'test',
        'first': 'first_image_tag',
        'second': 'second_image_tag',
    },
    SHUTTLE_ORDERHISTORY_ENABLED=True,
)
async def test_list_simple(
        mockserver,
        web_app_client,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        load_json,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_size_hint.json',
            'ridehistory_resp_simple.json',
        )

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'eats_oh_expected_req_simple.json',
            'eats_oh_resp_simple.json',
        )

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/booking/history/list',
    )
    async def handler_shuttle_control(request):
        return load_json('shuttle_control_resp.json')

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers=get_default_headers(),
        json=get_default_response(),
    )

    assert response.status == 200
    assert await response.json() == load_json('expected_resp_simple.json')


async def test_list_empty(
        taxi_orderhistory_web,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        load_json,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_simple.json',
            'ridehistory_resp_empty.json',
        )

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'eats_oh_expected_req_simple.json',
            'oh_resp_empty.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {
                'taxi': {'image_tags': {'skin_version': '6'}},
                'eats': {},
                'grocery': {},
            },
            'include_service_metadata': True,
        },
    )

    assert response.status == 200
    response_body = await response.json()
    expected = load_json('expected_resp_empty_with_sm.json')
    assert response_body == expected


@pytest.mark.config(SHUTTLE_ORDERHISTORY_ENABLED=True)
@pytest.mark.parametrize(
    'req_range, oh_expected_req, status',
    [
        ({}, 'empty', 200),
        ({'results': 3}, 'results', 200),
        (
            {
                'older_than': {
                    'taxi': {'created_at': 0, 'order_id': '0'},
                    'eats': {'created_at': 0, 'order_id': '0'},
                    'grocery': {'created_at': 0, 'order_id': '0'},
                    'shuttle': {'created_at': 0, 'order_id': '0'},
                },
            },
            'older_than',
            200,
        ),
        (
            {
                'older_than': {
                    'taxi': {'created_at': 0, 'order_id': '0'},
                    'eats': {'created_at': 0, 'order_id': '0'},
                    'grocery': {'created_at': 0, 'order_id': '0'},
                    'shuttle': {'created_at': 0, 'order_id': '0'},
                },
                'results': 3,
            },
            'results_older_than',
            200,
        ),
        ({'results': 1000}, '', 400),
    ],
)
async def test_list_range(
        taxi_orderhistory_web,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        load_json,
        req_range,
        oh_expected_req,
        status,
        mockserver,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            load_json('ridehistory_expected_reqs_range.json')[oh_expected_req],
            'ridehistory_resp_empty.json',
        )

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            load_json('eats_oh_expected_reqs_range.json')[oh_expected_req],
            'oh_resp_empty.json',
        )

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/booking/history/list',
    )
    async def handler_shuttle_control(request):
        return _default_handle_oh(
            request,
            load_json,
            load_json('shuttle_expected_reqs_range.json')[oh_expected_req],
            'ridehistory_resp_empty.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {
                'taxi': {'image_tags': {'skin_version': '6'}},
                'eats': {},
                'grocery': {},
                'shuttle': {},
            },
            'range': req_range,
        },
    )

    assert response.status == status


@pytest.mark.parametrize(
    'include_service_metadata, oh_expected_req, '
    'ridehistory_resp, eats_oh_resp, expected_response',
    [
        (
            True,
            'with_sm',
            'ridehistory_resp_sm.json',
            'eats_oh_resp_sm.json',
            'expected_resp_sm.json',
        ),
        (
            False,
            'without_sm',
            'ridehistory_resp_empty.json',
            'oh_resp_empty.json',
            'expected_resp_empty.json',
        ),
    ],
)
async def test_list_service_metadata(
        taxi_orderhistory_web,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        load_json,
        include_service_metadata,
        oh_expected_req,
        ridehistory_resp,
        eats_oh_resp,
        expected_response,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            load_json('ridehistory_expected_reqs_sm.json')[oh_expected_req],
            ridehistory_resp,
        )

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            load_json('eats_oh_expected_reqs_sm.json')[oh_expected_req],
            eats_oh_resp,
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {
                'taxi': {'image_tags': {'skin_version': '6'}},
                'eats': {},
                'grocery': {},
            },
            'include_service_metadata': include_service_metadata,
        },
    )

    assert response.status == 200
    response_body = await response.json()
    expected = load_json(expected_response)
    assert response_body == expected


async def test_list_pagination(
        taxi_orderhistory_web,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        load_json,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        request_body = request.json
        expected_requests = load_json(
            'ridehistory_expected_reqs_pagination.json',
        )
        if request_body == expected_requests['first']:
            return web.json_response(
                load_json('ridehistory_resp_pagination1.json'),
            )
        if request_body == expected_requests['second']:
            return web.json_response(
                load_json('ridehistory_resp_pagination2.json'),
            )

        assert request_body and False

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        request_body = request.json
        expected_requests = load_json('eats_oh_expected_reqs_pagination.json')
        if request_body == expected_requests['first']:
            return web.json_response(
                load_json('eats_oh_resp_pagination1.json'),
            )
        if request_body == expected_requests['second']:
            return web.json_response(
                load_json('eats_oh_resp_pagination2.json'),
            )

        assert request_body and False

    response1 = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {
                'taxi': {'image_tags': {'skin_version': '6'}},
                'eats': {},
                'grocery': {},
            },
            'range': {'results': 4},
        },
    )

    assert response1.status == 200
    response1_body = await response1.json()
    expected_1 = load_json('expected_resp_pagination1.json')
    assert response1_body == expected_1

    response2 = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {
                'taxi': {'image_tags': {'skin_version': '6'}},
                'eats': {},
                'grocery': {},
            },
            'range': {'results': 3, 'older_than': response1_body['cursor']},
        },
    )

    assert response2.status == 200
    assert await response2.json() == load_json(
        'expected_resp_pagination2.json',
    )


async def test_list_sort(
        taxi_orderhistory_web,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        load_json,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_sort.json',
            'ridehistory_resp_sort.json',
        )

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'eats_oh_expected_req_sort.json',
            'eats_oh_resp_sort.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {
                'taxi': {'image_tags': {'skin_version': '6'}},
                'eats': {},
                'grocery': {},
            },
        },
    )

    assert response.status == 200
    assert await response.json() == load_json('expected_resp_sort.json')


@pytest.mark.config(TAXI_ORDERHISTORY_ENABLED=False)
@pytest.mark.parametrize(
    'services, num_orders, eats_called',
    [(['taxi'], 0, 0), (['taxi', 'eats'], 6, 1)],
)
async def test_list_taxi_disabled(
        taxi_orderhistory_web,
        mock_eats_orderhistory_py3,
        load_json,
        services,
        num_orders,
        eats_called,
):
    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'eats_oh_expected_req_simple.json',
            'eats_oh_resp_simple.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {key: {} for key in services},
            'include_service_metadata': True,
        },
    )

    assert response.status == 200
    data = await response.json()
    assert len(data['orders']) == num_orders
    assert handler_eats.times_called == eats_called


@pytest.mark.config(EATS_ORDERHISTORY_ENABLED=False)
@pytest.mark.parametrize(
    'services, num_orders, taxi_called',
    [(['eats'], 0, 0), (['taxi', 'eats'], 10, 1)],
)
async def test_list_eats_disabled(
        taxi_orderhistory_web,
        mock_ridehistory,
        load_json,
        services,
        num_orders,
        taxi_called,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_simple.json',
            'ridehistory_resp_simple.json',
        )

    services = {key: {} for key in services}
    if 'taxi' in services:
        services['taxi'] = {'image_tags': {'skin_version': '6'}}

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={'services': services, 'include_service_metadata': True},
    )

    assert response.status == 200
    data = await response.json()
    assert len(data['orders']) == num_orders
    assert handler_taxi.times_called == taxi_called


@pytest.mark.parametrize(
    'accept_language, x_request_language, eats_name',
    [('ru-RU', 'ru', '<EATS_RU>'), ('en-EN', 'en', '<EATS_EN>')],
)
@pytest.mark.translations(
    client_messages={
        'superapp.eats.service_name': {'ru': '<EATS_RU>', 'en': '<EATS_EN>'},
    },
)
async def test_list_eats_sm_localization(
        taxi_orderhistory_web,
        mock_eats_orderhistory_py3,
        load_json,
        accept_language,
        x_request_language,
        eats_name,
):
    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return web.json_response(load_json('eats_oh_resp_sm.json'))

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': accept_language,
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': x_request_language,
        },
        json={
            'services': {'eats': {}, 'grocery': {}},
            'include_service_metadata': True,
        },
    )

    assert response.status == 200
    response_body = await response.json()
    service_metadata = response_body.get('service_metadata')
    assert service_metadata is not None
    for service_sm in service_metadata:
        service = service_sm['service']
        if service == 'eats':
            assert service_sm['name'] == eats_name
        else:
            assert False


PATCHED_BASE_URL = '$mockserver/override_url'


@pytest.mark.config(PAYMENTS_EDA_ATTEMPT_TO_PATCH_EDA_BASE_URL=True)
async def test_override_orderhistory_url(
        web_app_client, patch, mockserver, mock_ridehistory, load_json,
):
    @mockserver.json_handler('/override_url/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        assert request
        return web.json_response(load_json('eats_oh_resp_sm.json'))

    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return web.json_response(load_json('ridehistory_resp_empty.json'))

    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values(*args, **kwargs):
        return [
            experiments3.ExperimentsValue(
                name=experiments.EXP3_PAYMENTS_EDA_URLS,
                value={'patched_base_url': PATCHED_BASE_URL},
            ),
        ]

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={'services': {'taxi': {}, 'eats': {}, 'grocery': {}}},
    )

    assert response.status == 200


async def test_overall_older_than(
        taxi_orderhistory_web,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        load_json,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return web.json_response(load_json('ridehistory_resp_empty.json'))

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return web.json_response(load_json('eats_oh_resp_simple.json'))

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {'taxi': {}, 'eats': {}, 'grocery': {}},
            'range': {
                'older_than': {
                    'taxi': {'created_at': 1563284674, 'order_id': '777'},
                },
            },
        },
    )

    # 1563284674 is 2019-07-16T13:44:34+00:00
    # Though older_than constraint is only for taxi, we filter out all
    # newer orders from eats/grocery

    assert response.status == 200

    data = await response.json()
    order_ids = {o['data']['order_id'] for o in data['orders']}
    assert order_ids == {'id11', 'id9'}


async def test_pagination_inheritance(
        taxi_orderhistory_web,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        load_json,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return web.json_response(load_json('ridehistory_resp_empty.json'))

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return web.json_response(load_json('eats_oh_resp_simple.json'))

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {'taxi': {}, 'eats': {}, 'grocery': {}},
            'range': {
                'older_than': {
                    'taxi': {'created_at': 2000000001, 'order_id': '777'},
                    'eats': {'created_at': 2000000002, 'order_id': '777'},
                },
            },
        },
    )

    assert response.status == 200

    data = await response.json()

    # taxi is inherited from request
    assert data['cursor'] == {
        'taxi': {'created_at': 2000000001, 'order_id': '777'},
        'eats': {
            'created_at': 1563108275,
            'created_at_us': 1563108275000000,
            'order_id': 'id11',
        },
    }


@pytest.mark.parametrize(
    ('services', 'iiko_calls_count'),
    (
        pytest.param(
            {'taxi': {'image_tags': {'skin_version': '6'}}, 'qr_pay': {}},
            1,
            marks=pytest.mark.config(QR_ORDERHISTORY_ENABLED=True),
            id='normal work',
        ),
        pytest.param(
            {'taxi': {'image_tags': {'skin_version': '6'}}, 'qr_pay': {}},
            0,
            marks=pytest.mark.config(QR_ORDERHISTORY_ENABLED=False),
            id='qr orderhistory disabled',
        ),
    ),
)
async def test_with_qr_orders(
        taxi_orderhistory_web,
        mock_ridehistory,
        mock_iiko_integration,
        load_json,
        services,
        iiko_calls_count,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_simple.json',
            'ridehistory_resp_simple.json',
        )

    @mock_iiko_integration('/iiko-integration/v1/orderhistory/list')
    async def handler_qr(request):
        return _default_handle_oh(
            request,
            load_json,
            'qr_orderhistory_req.json',
            'qr_orderhistory_resp.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={'services': services, 'include_service_metadata': True},
    )

    assert response.status == 200
    assert handler_qr.times_called == iiko_calls_count
    if iiko_calls_count == 1:
        assert (await response.json()) == load_json(
            'expected_resp_with_qr.json',
        )


@pytest.mark.config(ORDERHISTORY_NEVER_FAIL_ENABLED=True)
@pytest.mark.parametrize(
    'fired_fallbacks, expected_response',
    [
        (
            [CORE_EATS_HANDLER_FALLBACK],
            'expected_resp_eats_grocery_fallback_fired.json',
        ),
        pytest.param(
            [CORE_EATS_HANDLER_FALLBACK],
            'expected_resp_eats_grocery_fallback_fired_translations.json',
            marks=pytest.mark.translations(
                client_messages={
                    'superapp.eats.service_name': {
                        'ru': '<EATS_RU>',
                        'en': '<EATS_EN>',
                    },
                    'superapp.grocery.service_name': {
                        'ru': '<GROCERY_RU>',
                        'en': '<GROCERY_EN>',
                    },
                },
            ),
        ),
        ([], 'expected_resp_eats_grocery_fallback_not_fired.json'),
    ],
)
async def test_eats_grocery_fallback(
        taxi_orderhistory_web,
        load_json,
        mock_ridehistory,
        mock_fallbacks,
        mock_eats_orderhistory_error,
        fired_fallbacks,
        expected_response,
):
    await mock_fallbacks(fired_fallbacks)

    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_simple.json',
            'ridehistory_resp_simple.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {
                'taxi': {'image_tags': {'skin_version': '6'}},
                'eats': {},
                'grocery': {},
            },
            'include_service_metadata': True,
        },
    )

    assert response.status == 200
    assert await response.json() == load_json(expected_response)


@pytest.mark.config(
    DRIVE_ORDERHISTORY_ENABLED=True,
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 0, 'drive': 2}},
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'}},
    client_messages={'a': {'b': 'c'}},
)
@pytest.mark.parametrize(
    [
        'flags',
        'drive_times_called',
        'drive_code',
        'expected_resp',
        'expected_error_counts',
    ],
    [
        (
            'portal',
            1,
            200,
            'expected_resp_with_drive.json',
            {
                'deser_DriveOrderShort': 2,
                'deser_ViewsItem': 1,
                'prepare_order_short': 1,
            },
        ),
        ('pdd', 1, 401, 'expected_resp_no_drive.json', {}),
        ('phonish', 0, None, 'expected_resp_no_drive.json', {}),
        (None, 0, None, 'expected_resp_no_drive.json', {}),
    ],
)
async def test_with_drive_orders(
        web_app_client,
        web_app,
        mock_ridehistory,
        mock_yandex_drive,
        mockserver,
        get_stats_by_label_values,
        load_json,
        flags,
        drive_times_called,
        drive_code,
        expected_resp,
        expected_error_counts,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return load_json('ridehistory_resp_simple.json')

    @mock_yandex_drive('/sessions/list')
    async def handler_drive(request):
        assert request.json == {'range': {'results': 77}}
        assert request.args['lang'] == 'ru'
        assert request.headers['X-Ya-User-Ticket'] == 'this-is-a-user-ticket'
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'uid0').hexdigest()
        )
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        if drive_code == 200:
            return load_json('drive_list_basic.json')
        return mockserver.make_response(
            status=drive_code,
            json={'code': 'error', 'message': 'error'},
            headers={'X-Req-Id': '123'},
        )

    headers = {
        'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
        'Accept-Language': 'ru-RU',
        'X-Yandex-UID': 'uid0',
        'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
        'X-Request-Language': 'ru',
        'X-Ya-User-Ticket': 'this-is-a-user-ticket',
    }
    if flags:
        headers.update({'X-YaTaxi-Pass-Flags': flags})

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers=headers,
        json={
            'services': {
                'taxi': {'image_tags': {'skin_version': '6'}},
                'drive': {},
            },
            'range': {'results': 77},
            'include_service_metadata': True,
        },
    )

    assert response.status == 200
    assert await response.json() == load_json(expected_resp)
    assert handler_drive.times_called == drive_times_called

    stats = get_stats_by_label_values(
        web_app['context'],
        {'sensor': 'orderhistory.drive.response_parsing_failure'},
    )
    error_counts = {s['labels']['type']: s['value'] for s in stats}
    assert error_counts == expected_error_counts


@pytest.mark.config(
    SCOOTERS_ORDERHISTORY_ENABLED=True,
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 0, 'drive': 2}},
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'}},
    client_messages={'a': {'b': 'c'}},
)
@pytest.mark.parametrize(
    [
        'flags',
        'drive_times_called',
        'drive_code',
        'expected_resp',
        'expected_error_counts',
    ],
    [
        (
            'portal',
            1,
            200,
            'expected_resp_with_scooters.json',
            {
                'deser_DriveOrderShort': 2,
                'deser_ViewsItem': 1,
                'prepare_order_short': 1,
            },
        ),
        ('pdd', 1, 401, 'expected_resp_no_drive.json', {}),
        ('phonish', 0, None, 'expected_resp_no_drive.json', {}),
        (None, 0, None, 'expected_resp_no_drive.json', {}),
    ],
)
async def test_with_scooters_orders(
        web_app_client,
        web_app,
        mock_ridehistory,
        mock_scooter_backend_sessions,
        mockserver,
        patch,
        get_stats_by_label_values,
        load_json,
        flags,
        drive_times_called,
        drive_code,
        expected_resp,
        expected_error_counts,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return load_json('ridehistory_resp_simple.json')

    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values(*args, **kwargs):
        return [
            experiments3.ExperimentsValue(
                name=experiments.EXP3_SCOOTERS_ORDERHISTORY_ENABLED,
                value={'enabled': True},
            ),
        ]

    @mock_scooter_backend_sessions('/sessions/list')
    async def handler_scooters(request):
        assert request.json == {'range': {'results': 42}}
        assert request.args['lang'] == 'ru'
        assert request.headers['X-Ya-User-Ticket'] == 'this-is-a-user-ticket'
        assert (
            request.headers['X-Ya-UserSplit-Id']
            == hashlib.md5(b'uid0').hexdigest()
        )
        assert 'IC-Taxi-App-Build' not in request.headers
        assert request.headers['AC-Taxi-App-Build'] == '1'
        assert request.headers['TC-Taxi-App-Build'] == '1'
        if drive_code == 200:
            return load_json('scooters_list_basic.json')
        return mockserver.make_response(
            status=drive_code,
            json={'code': 'error', 'message': 'error'},
            headers={'X-Req-Id': '123'},
        )

    headers = {
        'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
        'Accept-Language': 'ru-RU',
        'X-Yandex-UID': 'uid0',
        'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
        'X-Request-Language': 'ru',
        'X-Ya-User-Ticket': 'this-is-a-user-ticket',
    }
    if flags:
        headers.update({'X-YaTaxi-Pass-Flags': flags})

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers=headers,
        json={
            'services': {
                'taxi': {'image_tags': {'skin_version': '6'}},
                'scooters': {},
            },
            'range': {'results': 42},
            'include_service_metadata': True,
        },
    )

    assert response.status == 200
    assert await response.json() == load_json(expected_resp)
    assert handler_scooters.times_called == drive_times_called

    stats = get_stats_by_label_values(
        web_app['context'],
        {'sensor': 'orderhistory.scooters.response_parsing_failure'},
    )
    error_counts = {s['labels']['type']: s['value'] for s in stats}
    assert error_counts == expected_error_counts


@pytest.mark.config(
    TAXI_ORDERHISTORY_ENABLED=False,
    WIND_ORDERHISTORY_ENABLED=True,
    CURRENCY_FORMATTING_RULES={'ILS': {'__default__': 0, 'drive': 2}},
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'ru': '$SIGN$$VALUE$ $CURRENCY$'}},
    client_messages={'a': {'b': 'c'}},
)
@pytest.mark.parametrize(
    [
        'talaria_times_called',
        'resp_code',
        'expected_resp',
        'expected_error_counts',
    ],
    [
        (
            1,
            200,
            'expected_resp_with_wind_scooters.json',
            {
                'deser_DriveOrderShort': 2,
                'deser_ViewsItem': 1,
                'prepare_order_short': 1,
            },
        ),
    ],
)
async def test_with_wind_orders(
        web_app_client,
        web_app,
        mockserver,
        patch,
        mock_talaria_misc,
        get_stats_by_label_values,
        load_json,
        talaria_times_called,
        resp_code,
        expected_resp,
        expected_error_counts,
):
    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values(*args, **kwargs):
        return [
            experiments3.ExperimentsValue(
                name=experiments.EXP3_WIND_ORDERHISTORY_ENABLED,
                value={'enabled': True},
            ),
        ]

    @mock_talaria_misc('/talaria/v1/ride-history/list')
    async def _mock_talaria_ride_history_list(request):
        assert request.json == {
            'yandex_user_info': {
                'personal_phone_id': 'personal_phone_id',
                'yandex_uid': 'uid0',
            },
            'range': {'results': 42},
        }
        if resp_code == 200:
            return load_json('talaria_ride_history_resp_basic.json')
        return mockserver.make_response(
            status=resp_code,
            json={'code': 'error', 'message': 'error'},
            headers={'X-Req-Id': '123'},
        )

    headers = {
        'X-YaTaxi-User': 'personal_phone_id=personal_phone_id',
        'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
        'Accept-Language': 'ru-RU',
        'X-Yandex-UID': 'uid0',
        'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
        'X-Request-Language': 'ru',
    }

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers=headers,
        json={
            'services': {'wind': {}},
            'range': {'results': 42},
            'include_service_metadata': True,
        },
    )

    assert response.status == 200
    assert await response.json() == load_json(expected_resp)
    assert _mock_talaria_ride_history_list.times_called == talaria_times_called

    # stats = get_stats_by_label_values(
    #     web_app['context'],
    #     {'sensor': 'orderhistory.scooters.response_parsing_failure'},
    # )
    # error_counts = {s['labels']['type']: s['value'] for s in stats}
    # assert error_counts == expected_error_counts


@pytest.mark.config(
    ORDERHISTORY_SERVICE_IMAGE_TAGS={
        '__default__': 'test',
        'first': 'first_image_tag',
        'second': 'second_image_tag',
        '__brand_override__': {
            'some_brand': {
                'first': 'fourth_image_tag',
                'third': 'third_image_tag',
            },
        },
    },
)
async def test_brand_image_tag_override(
        taxi_orderhistory_web,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        load_json,
):
    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android,app_brand=some_brand',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={'services': {}},
    )

    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_brand_image_tag_override.json',
    )


@pytest.mark.config(
    GROCERY_ORDERHISTORY_ENABLED=True, EATS_ORDERHISTORY_ENABLED=False,
)
async def test_with_grocery_orders(
        taxi_orderhistory_web,
        mock_ridehistory,
        mock_grocery_order_log,
        load_json,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return load_json('ridehistory_resp_sort.json')

    @mock_grocery_order_log('/internal/orders/v1/retrieve')
    async def handler_eats(request):
        assert request.headers['X-Request-Application'] == 'app_name=android'
        return _default_handle_eats_oh(
            request,
            load_json,
            'grocery_oh_expected_req_simple.json',
            'grocery_oh_resp_simple.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {
                'taxi': {
                    'image_tags': {'skin_version': '6', 'size_hint': 9999},
                },
                'eats': {},
                'grocery': {},
            },
            'include_service_metadata': False,
        },
    )

    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_ride_and_grocery.json',
    )


@pytest.mark.config(GROCERY_ORDERHISTORY_ENABLED=True)
async def test_grocery_non_available_eats(
        taxi_orderhistory_web,
        mock_eats_orderhistory_py3,
        mock_grocery_order_log,
        mock_fallbacks,
        mockserver,
        load_json,
):
    await mock_fallbacks([CORE_EATS_HANDLER_FALLBACK])

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return mockserver.make_response('internal error', status=500)

    @mock_grocery_order_log('/internal/orders/v1/retrieve')
    async def handler_grocery(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'grocery_oh_expected_req_simple.json',
            'grocery_oh_resp_simple.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {'eats': {}, 'grocery': {}},
            'include_service_metadata': False,
        },
    )

    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_grocery_with_eats_fallback.json',
    )


@pytest.mark.config(GROCERY_ORDERHISTORY_ENABLED=True)
async def test_grocery_orders_sm(
        taxi_orderhistory_web,
        mock_eats_orderhistory_py3,
        mock_grocery_order_log,
        load_json,
):
    @mock_grocery_order_log('/internal/orders/v1/retrieve')
    async def handler_grocery(request):
        return load_json('grocery_oh_resp_sm.json')

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={'services': {'grocery': {}}, 'include_service_metadata': True},
    )

    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_eats_and_grocery_sm.json',
    )


@pytest.mark.config(
    GROCERY_ORDERHISTORY_ENABLED=True, EATS_ORDERHISTORY_ENABLED=False,
)
async def test_grocery_older_than(
        taxi_orderhistory_web, mock_grocery_order_log, load_json,
):
    @mock_grocery_order_log('/internal/orders/v1/retrieve')
    async def handler_grocery(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'grocery_oh_expected_req_older_than.json',
            'grocery_oh_resp_simple.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b726',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {'grocery': {}},
            'range': {
                'older_than': {
                    'grocery_standalone': {
                        'created_at': 1563284674,
                        'order_id': 'grocery_order_id',
                    },
                },
            },
        },
    )
    assert response.status == 200


GROCERY_FALLBACK = (
    'handler.grocery-order-log./internal/orders/v1/retrieve-POST.fallback'
)


@pytest.mark.config(
    GROCERY_ORDERHISTORY_ENABLED=True, EATS_ORDERHISTORY_ENABLED=False,
)
async def test_grocery_fallback(
        taxi_orderhistory_web,
        load_json,
        mock_fallbacks,
        mock_grocery_order_log,
        mockserver,
):
    await mock_fallbacks([GROCERY_FALLBACK])

    @mock_grocery_order_log('/internal/orders/v1/retrieve')
    async def handler_drive(request):
        return mockserver.make_response(status=500, json={})

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
            'X-Ya-User-Ticket': 'this-is-a-user-ticket',
            'X-YaTaxi-Pass-Flags': 'portal',
        },
        json={'services': {'grocery': {}}, 'include_service_metadata': True},
    )

    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_grocery_fallback.json',
    )


# test sorted by last_order_created_at
@pytest.mark.config(GROCERY_ORDERHISTORY_ENABLED=True)
async def test_eats_and_grocery_sm(
        taxi_orderhistory_web,
        mock_eats_orderhistory_py3,
        mock_grocery_order_log,
        mockserver,
):
    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    def handler_eats(request):
        return mockserver.make_response(
            status=200,
            json={
                'service_metadata': [
                    {
                        'last_order_created_at': '2019-07-24T17:00:00+03:00',
                        'last_order_id': 'eats_grocery_id1',
                        'name': 'Лавка',
                        'service': 'grocery',
                    },
                ],
            },
        )

    @mock_grocery_order_log('/internal/orders/v1/retrieve')
    async def handler_grocery(request):
        return mockserver.make_response(
            status=200,
            json={
                'orders': [],
                'service_metadata': {
                    'last_order_created_at': '2019-07-25T17:00:00+03:00',
                    'last_order_id': 'grocery_id1',
                    'name': 'Лавка',
                },
            },
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={'services': {'grocery': {}}, 'include_service_metadata': True},
    )

    assert response.status == 200
    data = await response.json()
    assert len(data['service_metadata']) == 1
    assert data['service_metadata'][0]['last_order_id'] == 'grocery_id1'


@pytest.mark.translations(
    client_messages={
        'superapp.delivery.service_name': {
            'ru': '<DELIVERY_RU>',
            'en': '<DELIVERY_EN>',
        },
    },
)
@pytest.mark.config(DELIVERY_ORDERHISTORY_ENABLED=True)
async def test_delivery_simple(
        taxi_orderhistory_web, mock_cargo_c2c, load_json,
):
    @mock_cargo_c2c('/orderhistory/v1/list')
    async def handler_cargo_c2c(request):
        assert request.json == {'range': {'results': 10}}
        return {
            'deliveries': [
                {
                    'delivery_id': 'cargo-claims/123',
                    'created_at': '2019-07-22T13:44:34+00:00',
                    'key': 'value',
                },
            ],
            'service_metadata': {
                'service': 'service_will_be_ignored',
                'name': 'name__will_be_ignored',
                'flavor': 'flavor_will_be_ignored',
                'last_order_id': 'cargo-claims/123',
                'last_order_created_at': '2019-07-22T13:44:34+00:00',
            },
        }

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={'services': {'delivery': {}}, 'include_service_metadata': True},
    )

    assert await response.json() == load_json('expected_resp_delivery.json')
    assert handler_cargo_c2c.times_called == 1


@pytest.mark.translations(
    client_messages={
        'superapp.taxi.service_name': {'ru': '<TAXI_RU>', 'en': '<TAXI_EN>'},
    },
)
@pytest.mark.config(DELIVERY_ORDERHISTORY_ENABLED=True)
async def test_delivery_legacy_simple(
        taxi_orderhistory_web, mock_cargo_c2c, mock_ridehistory, load_json,
):
    @mock_cargo_c2c('/orderhistory/v1/list')
    async def handler_cargo_c2c(request):
        assert request.json == {'range': {'results': 10}}
        return {
            'deliveries': [
                {
                    'delivery_id': 'cargo-claims/123',
                    'created_at': '2019-07-16T16:44:33+03:00',
                    'key': 'value',
                },
            ],
            'service_metadata': {
                'service': 'service_will_be_ignored',
                'flavor': 'flavor_will_be_ignored',
                'name': 'name_will_be_ignored',
                'last_order_id': 'cargo-claims/123',
                'last_order_created_at': '2019-07-16T16:44:33+03:00',
            },
        }

    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_simple.json',
            'ridehistory_resp_empty.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {'taxi': {'image_tags': {'skin_version': '6'}}},
            'include_service_metadata': True,
        },
    )

    assert await response.json() == load_json(
        'expected_resp_delivery_legacy.json',
    )

    assert handler_cargo_c2c.times_called == 1


@pytest.mark.translations(
    client_messages={
        'superapp.delivery.service_name': {
            'ru': '<DELIVERY_RU>',
            'en': '<DELIVERY_EN>',
        },
    },
)
@pytest.mark.config(DELIVERY_ORDERHISTORY_ENABLED=True)
async def test_delivery_older_than(
        taxi_orderhistory_web, mock_cargo_c2c, load_json,
):
    @mock_cargo_c2c('/orderhistory/v1/list')
    async def handler_cargo_c2c(request):
        assert request.json == {
            'range': {
                'older_than': {
                    'created_at': '2019-07-15T16:44:34+03:00',
                    'delivery_id': 'cargo-claims/123',
                },
                'results': 10,
            },
        }

        return {
            'deliveries': [
                {
                    'delivery_id': 'cargo-claims/11',
                    'created_at': '2019-07-14T05:14:34+00:00',
                    'key': 'value',
                },
            ],
            'service_metadata': {
                'service': 'service_will_be_ignored',
                'flavor': 'flavor_will_be_ignored',
                'name': 'name_will_be_ignored',
                'last_order_id': 'cargo-claims/11',
                'last_order_created_at': '2019-07-14T05:14:34+00:00',
            },
        }

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {'delivery': {}},
            'range': {
                'results': 10,
                'older_than': {
                    'delivery': {
                        'created_at': 1563198274,
                        'order_id': 'cargo-claims/123',
                    },
                },
            },
            'include_service_metadata': True,
        },
    )

    assert await response.json() == load_json(
        'expected_resp_delivery_older_than.json',
    )
    assert handler_cargo_c2c.times_called == 1


@pytest.mark.translations(
    client_messages={
        'superapp.taxi.service_name': {'ru': '<TAXI_RU>', 'en': '<TAXI_EN>'},
    },
)
@pytest.mark.config(DELIVERY_ORDERHISTORY_ENABLED=True)
async def test_delivery_legacy_older_than(
        taxi_orderhistory_web, mock_cargo_c2c, load_json, mock_ridehistory,
):
    @mock_cargo_c2c('/orderhistory/v1/list')
    async def handler_cargo_c2c(request):
        assert request.json == {
            'range': {
                'older_than': {
                    'created_at': '2019-07-16T16:44:34+03:00',
                    'delivery_id': 'taxi/123',
                },
                'results': 10,
            },
        }

        return {
            'deliveries': [
                {
                    'delivery_id': 'cargo-claims/123',
                    'created_at': '2019-07-16T16:44:33+03:00',
                    'key': 'value',
                },
                {
                    'delivery_id': 'cargo-claims/456',
                    'created_at': '2019-07-16T16:44:34+03:00',
                    'key': 'value',
                },
            ],
            'service_metadata': {
                'service': 'service_will_be_ignored',
                'flavor': 'flavor_will_be_ignored',
                'name': 'name_will_be_ignored',
                'last_order_id': 'cargo-claims/123',
                'last_order_created_at': '2019-07-16T16:44:33+03:00',
            },
        }

    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_simple.json',
            'ridehistory_resp_empty.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {'taxi': {'image_tags': {'skin_version': '6'}}},
            'range': {
                'results': 10,
                'older_than': {
                    'taxi_delivery': {
                        'created_at': 1563284674,
                        'order_id': 'taxi/123',
                    },
                },
            },
            'include_service_metadata': True,
        },
    )

    assert await response.json() == load_json(
        'expected_resp_delivery_legacy.json',
    )
    assert handler_cargo_c2c.times_called == 1


DELIVERY_FALLBACK = 'handler.cargo-c2c./orderhistory/v1/list-POST.fallback'


@pytest.mark.config(DELIVERY_ORDERHISTORY_ENABLED=True)
async def test_delivery_fallback(
        taxi_orderhistory_web,
        load_json,
        mockserver,
        mock_cargo_c2c,
        mock_fallbacks,
        mock_ridehistory,
):
    await mock_fallbacks([DELIVERY_FALLBACK])

    @mock_cargo_c2c('/orderhistory/v1/list')
    async def handler_cargo_c2c(request):
        return mockserver.make_response(
            status=500,
            json={'code': '500', 'message': '500'},
            headers={'X-Req-Id': '123'},
        )

    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_simple.json',
            'ridehistory_resp_empty.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
            'X-Ya-User-Ticket': 'this-is-a-user-ticket',
            'X-YaTaxi-Pass-Flags': 'portal',
        },
        json={'services': {'delivery': {}}, 'include_service_metadata': True},
    )

    assert response.status == 200
    assert await response.json() == {
        'cursor': {
            'failed_services': [{'id': 'delivery', 'name': 'Delivery'}],
        },
        'error_services': [],
        'fallback_services': [{'id': 'delivery', 'name': 'Delivery'}],
        'orders': [],
        'service_image_tags': {'__default__': 'nonexistent'},
        'service_metadata': [],
    }


@pytest.mark.config(DELIVERY_ORDERHISTORY_ENABLED=True)
async def test_delivery_legacy_fallback(
        taxi_orderhistory_web,
        load_json,
        mockserver,
        mock_cargo_c2c,
        mock_fallbacks,
        mock_ridehistory,
):
    await mock_fallbacks([DELIVERY_FALLBACK])

    @mock_cargo_c2c('/orderhistory/v1/list')
    async def handler_cargo_c2c(request):
        return mockserver.make_response(
            status=500,
            json={'code': '500', 'message': '500'},
            headers={'X-Req-Id': '123'},
        )

    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_simple.json',
            'ridehistory_resp_empty.json',
        )

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
            'X-Ya-User-Ticket': 'this-is-a-user-ticket',
            'X-YaTaxi-Pass-Flags': 'portal',
        },
        json={
            'services': {'taxi': {'image_tags': {'skin_version': '6'}}},
            'include_service_metadata': True,
        },
    )

    assert response.status == 200
    assert await response.json() == {
        'cursor': {
            'failed_services': [
                {'id': 'taxi', 'flavor': 'delivery', 'name': 'Delivery'},
            ],
        },
        'error_services': [],
        'fallback_services': [
            {'id': 'taxi', 'flavor': 'delivery', 'name': 'Delivery'},
        ],
        'orders': [],
        'service_image_tags': {'__default__': 'nonexistent'},
        'service_metadata': [],
    }


@pytest.mark.config(
    DELIVERY_ORDERHISTORY_ENABLED=True, TAXI_ORDERHISTORY_ENABLED=True,
)
@pytest.mark.parametrize(
    'taxi_last_order_created_at',
    ['2019-07-22T16:44:33+03:00', '2019-07-22T16:44:35+03:00'],
)
async def test_delivery_legacy_taxi_service_metadata(
        taxi_orderhistory_web,
        mock_cargo_c2c,
        mock_ridehistory,
        load_json,
        taxi_last_order_created_at,
):
    @mock_cargo_c2c('/orderhistory/v1/list')
    async def handler_cargo_c2c(request):
        assert request.json == {'range': {'results': 10}}
        return {
            'deliveries': [
                {
                    'delivery_id': 'cargo-claims/123',
                    'created_at': '2019-07-22T13:44:34+00:00',
                    'key': 'value',
                },
            ],
            'service_metadata': {
                'service': 'taxi',
                'flavor': 'delivery',
                'name': 'Такси',
                'last_order_id': 'cargo-claims/123',
                'last_order_created_at': '2019-07-22T13:44:34+00:00',
            },
        }

    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        resp = load_json('ridehistory_resp_sm.json')
        resp['service_metadata'][
            'last_order_created_at'
        ] = taxi_last_order_created_at

        return resp

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {'taxi': {'image_tags': {'skin_version': '6'}}},
            'include_service_metadata': True,
        },
    )

    service_metadatas = (await response.json())['service_metadata']
    assert len(service_metadatas) == 1
    service_metadata = service_metadatas[0]

    assert service_metadata['service'] == 'taxi'


@pytest.mark.config(
    DELIVERY_ORDERHISTORY_ENABLED=True,
    TAXI_ORDERHISTORY_ENABLED=True,
    EATS_ORDERHISTORY_ENABLED=True,
    QR_ORDERHISTORY_ENABLED=True,
    DRIVE_ORDERHISTORY_ENABLED=True,
    GROCERY_ORDERHISTORY_ENABLED=True,
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 0, 'drive': 2}},
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'}},
    client_messages={'a': {'ru': 'b'}},
)
@pytest.mark.parametrize(
    'never_fail_enabled',
    [
        False,
        pytest.param(
            True,
            marks=pytest.mark.config(ORDERHISTORY_NEVER_FAIL_ENABLED=True),
        ),
    ],
)
@pytest.mark.parametrize(
    [
        'request_services',
        'error_services',
        'expected_error_services',
        'expected_resp_services',
    ],
    [
        (
            ['taxi', 'eats', 'qr_pay', 'drive', 'grocery'],
            set(),
            set(),
            {
                ('taxi', None),
                ('taxi', 'delivery'),
                ('eats', None),
                ('qr_pay', None),
                ('drive', None),
                ('grocery', 'standalone'),
            },
        ),
        (
            ['taxi', 'eats', 'qr_pay', 'drive', 'grocery'],
            {'eats'},
            {('eats', None)},
            {
                ('taxi', None),
                ('taxi', 'delivery'),
                ('qr_pay', None),
                ('drive', None),
                ('grocery', 'standalone'),
            },
        ),
        (
            ['taxi', 'eats', 'qr_pay', 'drive', 'grocery'],
            {
                'cargo_c2c',
                'ridehistory',
                'eats',
                'standalone_grocery',
                'drive',
                'qr_pay',
            },
            {
                ('taxi', None),
                ('taxi', 'delivery'),
                ('eats', None),
                ('qr_pay', None),
                ('drive', None),
                ('grocery', 'standalone'),
            },
            set(),
        ),
        (
            ['taxi', 'eats', 'grocery', 'qr_pay'],
            {'cargo_c2c'},
            {('taxi', 'delivery')},
            {
                ('taxi', None),
                ('eats', None),
                ('grocery', 'standalone'),
                ('qr_pay', None),
            },
        ),
        (
            ['taxi', 'eats', 'grocery', 'qr_pay'],
            {'ridehistory'},
            {('taxi', None)},
            {
                ('taxi', 'delivery'),
                ('eats', None),
                ('grocery', 'standalone'),
                ('qr_pay', None),
            },
        ),
        (['eats'], {'eats'}, {('eats', None)}, set()),
        (['grocery'], set(), set(), {('grocery', 'standalone')}),
        (
            ['grocery'],
            {'standalone_grocery'},
            {('grocery', 'standalone')},
            set(),
        ),
        (['drive'], {'drive'}, {('drive', None)}, set()),
        (['qr_pay'], {'qr_pay'}, {('qr_pay', None)}, set()),
    ],
)
async def test_never_fail(
        web_app_client,
        web_app,
        mock_all_services,
        get_stats_by_label_values,
        request_services,
        error_services,
        expected_error_services,
        expected_resp_services,
        never_fail_enabled,
):
    mock_all_services(error_services)

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
            'X-YaTaxi-Pass-Flags': 'portal',
        },
        json={
            'services': {service: {} for service in request_services},
            'range': {'results': 77},
        },
    )

    if not never_fail_enabled and error_services:
        assert response.status == 500

        return

    assert response.status == 200

    response_json = await response.json()
    response_services = {
        (order['service'], order.get('flavor'))
        for order in response_json['orders']
    }
    assert response_services == expected_resp_services

    response_error_services = {
        (service['id'], service.get('flavor'))
        for service in response_json['error_services']
    }
    assert response_error_services == expected_error_services

    stats = get_stats_by_label_values(
        web_app['context'],
        {'sensor': 'orderhistory.never_fail.service_error'},
    )
    error_counts = {
        (s['labels']['service_id'], s['labels']['flavor']): s['value']
        for s in stats
    }
    assert error_counts == {
        (s[0], s[1] or 'default'): 1 for s in expected_error_services
    }


@pytest.mark.config(
    DELIVERY_ORDERHISTORY_ENABLED=True,
    TAXI_ORDERHISTORY_ENABLED=True,
    EATS_ORDERHISTORY_ENABLED=True,
    QR_ORDERHISTORY_ENABLED=True,
    DRIVE_ORDERHISTORY_ENABLED=True,
    GROCERY_ORDERHISTORY_ENABLED=True,
    CURRENCY_FORMATTING_RULES={'RUB': {'__default__': 2, 'drive': 2}},
)
@pytest.mark.translations(
    tariff={'currency_with_sign.default': {'ru': '$VALUE$ $SIGN$$CURRENCY$'}},
    client_messages={'a': {'ru': 'b'}},
)
@pytest.mark.parametrize(
    'never_fail_enabled',
    [
        False,
        pytest.param(
            True,
            marks=pytest.mark.config(ORDERHISTORY_NEVER_FAIL_ENABLED=True),
        ),
    ],
)
@pytest.mark.parametrize(
    [
        'request_services',
        'request_failed_services',
        'error_services',
        'expected_cursor_services',
        'expected_resp_services',
        'expected_handlers_called',
    ],
    [
        (
            {'taxi': {}, 'eats': {}, 'qr_pay': {}, 'drive': {}, 'grocery': {}},
            [],
            set(),
            set(),
            {
                ('taxi', None),
                ('taxi', 'delivery'),
                ('eats', None),
                ('qr_pay', None),
                ('drive', None),
                ('grocery', 'standalone'),
            },
            {
                'cargo_c2c',
                'ridehistory',
                'eats',
                'standalone_grocery',
                'drive',
                'qr_pay',
            },
        ),
        (
            {
                'taxi': {'flavors': ['delivery']},
                'eats': {},
                'qr_pay': {},
                'drive': {},
                'grocery': {'flavors': ['default']},
            },
            [],
            set(),
            set(),
            {
                ('taxi', 'delivery'),
                ('eats', None),
                ('qr_pay', None),
                ('drive', None),
            },
            {'cargo_c2c', 'eats', 'drive', 'qr_pay'},
        ),
        (
            {
                'taxi': {'flavors': ['delivery']},
                'eats': {},
                'qr_pay': {},
                'drive': {},
                'grocery': {'flavors': ['default']},
            },
            [],
            {'eats'},
            {('eats', None)},
            {('taxi', 'delivery'), ('qr_pay', None), ('drive', None)},
            {'cargo_c2c', 'eats', 'drive', 'qr_pay'},
        ),
        (
            {
                'taxi': {'flavors': ['delivery']},
                'eats': {},
                'qr_pay': {},
                'drive': {},
                'grocery': {'flavors': ['default']},
            },
            [{'id': 'qr_pay', 'name': '1'}],
            {'eats'},
            {('eats', None), ('qr_pay', None)},
            {('taxi', 'delivery'), ('drive', None)},
            {'cargo_c2c', 'eats', 'drive'},
        ),
    ],
)
async def test_never_fail_cursor(
        web_app_client,
        web_app,
        mock_all_services,
        get_stats_by_label_values,
        request_services,
        request_failed_services,
        error_services,
        expected_cursor_services,
        expected_resp_services,
        expected_handlers_called,
        never_fail_enabled,
):
    service_handler = mock_all_services(error_services)

    request_json = {'services': request_services, 'range': {'results': 77}}
    if request_failed_services:
        request_json['range']['older_than'] = {
            'failed_services': request_failed_services,
        }

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
            'X-YaTaxi-Pass-Flags': 'portal',
        },
        json=request_json,
    )

    if not never_fail_enabled and error_services:
        assert response.status == 500

        return

    assert response.status == 200

    response_json = await response.json()
    response_services = {
        (order['service'], order.get('flavor'))
        for order in response_json['orders']
    }
    assert response_services == expected_resp_services

    response_cursor_services = {
        (service['id'], service.get('flavor'))
        for service in response_json['cursor'].get('failed_services', [])
    }
    assert response_cursor_services == expected_cursor_services

    assert _get_handlers_called(service_handler) == expected_handlers_called


@pytest.mark.config(
    MARKET_ORDERHISTORY_ENABLED=True, ORDERHISTORY_NEVER_FAIL_ENABLED=True,
)
@pytest.mark.parametrize(
    [
        'market_resp',
        'body_extra',
        'add_user_ticket',
        'exp_market_req_body',
        'exp_resp_code',
        'exp_resp',
        'exp_market_times_called',
    ],
    [
        (
            'market_resp_simple.json',
            {},
            True,
            {'params': [{'pageSize': 10, 'returnAllOrders': False}]},
            200,
            'expected_resp_market.json',
            1,
        ),
        (None, {}, False, None, 200, 'expected_resp_market_error.json', 0),
        (
            'market_resp_empty.json',
            {},
            True,
            {'params': [{'pageSize': 10, 'returnAllOrders': True}]},
            200,
            'expected_resp_market_empty.json',
            1,
        ),
        (
            'market_resp_error.json',
            {},
            True,
            {'params': [{'pageSize': 10, 'returnAllOrders': False}]},
            200,
            'expected_resp_market_error.json',
            1,
        ),
        (
            'market_resp_simple.json',
            {
                'range': {
                    'older_than': {
                        'market': {
                            'created_at': 1624986308,
                            'created_at_us': 1624986308123000,
                            'order_id': '777',
                        },
                    },
                    'results': 20,
                },
            },
            True,
            {
                'params': [
                    {
                        'pageSize': 20,
                        'cursor': {
                            'toTimestamp': 1624986308123,
                            'toOrderId': 777,
                        },
                        'returnAllOrders': True,
                    },
                ],
            },
            200,
            'expected_resp_market_cursor.json',
            1,
        ),
        (
            None,
            {
                'range': {
                    'older_than': {
                        'market': {
                            'created_at': 1624986307,
                            'order_id': '777',
                        },
                    },
                    'results': 20,
                },
            },
            True,
            None,
            200,
            'expected_resp_market_error_cursor.json',
            0,
        ),
    ],
)
async def test_market_simple(
        web_app_client,
        patch,
        mock_market_orderhistory,
        mock_ridehistory,
        load_json,
        market_resp,
        body_extra,
        add_user_ticket,
        exp_market_req_body,
        exp_resp_code,
        exp_resp,
        exp_market_times_called,
):
    @mock_market_orderhistory('/api/v1')
    async def handler_market(request):
        assert request.query['name'] == 'resolveGoOrderHistoryList'
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket_777'
        assert request.headers['Api-Platform'] == 'go_orderhistory'
        assert request.json == exp_market_req_body

        return load_json(market_resp)

    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return load_json('ridehistory_resp_one.json')

    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values(*args, **kwargs):
        return [
            experiments3.ExperimentsValue(
                name=experiments.EXP3_MARKET_ORDERHISTORY_ENABLED,
                value={'enabled': True},
            ),
            experiments3.ExperimentsValue(
                name=experiments.EXP3_MARKET_ORDERHISTORY_ALL_ORDERS_ENABLED,
                value={
                    'enabled': (
                        exp_market_req_body['params'][0]['returnAllOrders']
                        if exp_market_req_body
                        else False
                    ),
                },
            ),
        ]

    request_json = {
        'services': {
            'taxi': {'image_tags': {'skin_version': '6'}},
            'market': {},
        },
        'include_service_metadata': not body_extra.get('range', {}).get(
            'older_than',
        ),
    }
    request_json.update(body_extra)

    request_headers = {
        'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
        'Accept-Language': 'ru-RU',
        'X-Yandex-UID': 'uid0',
        'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
        'X-Request-Application': 'app_name=android',
        'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
        'X-Request-Language': 'ru',
    }
    if add_user_ticket:
        request_headers['X-Ya-User-Ticket'] = 'user_ticket_777'

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers=request_headers,
        json=request_json,
    )

    assert response.status == exp_resp_code
    if exp_resp:
        assert await response.json() == load_json(exp_resp)

    assert handler_market.times_called == exp_market_times_called
    assert handler_taxi.times_called == 1


@pytest.mark.config(
    EATS_ORDERHISTORY_ENABLED=True, ORDERHISTORY_NEVER_FAIL_ENABLED=True,
)
@pytest.mark.parametrize(
    [
        'experiments_response',
        'exp_eats_orders_info_times_called',
        'exp_eats_orderhistory_times_called',
    ],
    [
        pytest.param(
            [
                experiments3.ExperimentsValue(
                    name=experiments.EXP3_EATS_ORDERS_INFO_ENABLED,
                    value={'enabled': True},
                ),
            ],
            1,
            0,
        ),
        ([], 0, 1),
    ],
)
@pytest.mark.parametrize(
    'fired_fallbacks',
    [[CORE_EATS_HANDLER_FALLBACK], [EATS_ORDERS_INFO_HANDLER_FALLBACK], []],
)
@pytest.mark.parametrize('is_eats_error', [True, False])
async def test_eats_orders_info(
        patch,
        mockserver,
        load_json,
        web_app_client,
        mock_eats_orders_info,
        mock_eats_orderhistory_py3,
        mock_fallbacks,
        experiments_response,
        exp_eats_orders_info_times_called,
        exp_eats_orderhistory_times_called,
        fired_fallbacks,
        is_eats_error,
):
    await mock_fallbacks(fired_fallbacks)

    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values(*args, **kwargs):
        return experiments_response

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def eats_orderhistory_mock(request):
        if is_eats_error:
            return mockserver.make_response(
                status=400, json={'error': 'error', 'message': 'message'},
            )

        return load_json('eats_oh_resp_simple.json')

    @mock_eats_orders_info('/internal/eats-orders-info/v1/retrieve')
    async def eats_orders_info_mock(request):
        if is_eats_error:
            return mockserver.make_response(
                status=400, json={'error': 'error', 'message': 'message'},
            )

        return load_json('eats_oh_resp_simple.json')

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Request-Language': 'ru',
        },
        json={'services': {'eats': {}}, 'include_service_metadata': True},
    )

    assert response.status == 200
    assert (
        eats_orderhistory_mock.times_called
        == exp_eats_orderhistory_times_called
    )
    assert (
        eats_orders_info_mock.times_called == exp_eats_orders_info_times_called
    )

    if not is_eats_error:
        exp_resp = 'expected_resp_eats.json'
    elif (
        exp_eats_orders_info_times_called == 1
        and EATS_ORDERS_INFO_HANDLER_FALLBACK in fired_fallbacks
    ):
        exp_resp = 'expected_resp_eats_fallback.json'
    elif (
        exp_eats_orderhistory_times_called == 1
        and CORE_EATS_HANDLER_FALLBACK in fired_fallbacks
    ):
        exp_resp = 'expected_resp_eats_fallback.json'
    else:
        exp_resp = 'expected_resp_eats_error.json'

    assert await response.json() == load_json(exp_resp)


@pytest.mark.parametrize(
    'market_locals_calls_count',
    (
        pytest.param(
            1,
            marks=pytest.mark.config(MARKET_LOCALS_ORDERHISTORY_ENABLED=True),
            id='normal work',
        ),
        pytest.param(
            0,
            marks=pytest.mark.config(MARKET_LOCALS_ORDERHISTORY_ENABLED=False),
            id='market_locals orderhistory disabled',
        ),
    ),
)
async def test_with_market_locals_orders(
        taxi_orderhistory_web,
        patch,
        mockserver,
        mock_ridehistory,
        load_json,
        market_locals_calls_count,
):
    @mock_ridehistory('/v2/list')
    async def _handler_taxi(request):
        return load_json('ridehistory_resp_one.json')

    @mockserver.json_handler(
        '/market-locals-orderhistory/api/v1/order/user/search/yg',
    )
    async def _handler(request):
        assert request.query['seek'] == '777'
        assert request.query['count'] == '20'
        assert request.headers['X-Ya-User-Ticket'] == 'user_ticket_777'
        return load_json('market_locals_resp.json')

    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values_(*args, **kwargs):
        return [
            experiments3.ExperimentsValue(
                name=experiments.EXP3_MARKET_LOCALS_ORDERHISTORY_ENABLED,
                value={'enabled': True},
            ),
        ]

    # for some reason @patch doesn't work
    @mockserver.json_handler('/experiments3/v1/experiments')
    def _match(request):
        return {
            'items': [
                {
                    'name': (
                        experiments.EXP3_MARKET_LOCALS_ORDERHISTORY_ENABLED
                    ),
                    'value': {'enabled': True},
                },
            ],
        }

    response = await taxi_orderhistory_web.post(
        '/4.0/orderhistory/v2/list',
        headers={
            'X-YaTaxi-UserId': '9e0a6783132f8d50e40acb8c7e6b7268',
            'Accept-Language': 'ru-RU',
            'X-Yandex-UID': 'uid0',
            'X-YaTaxi-Bound-Uids': 'uid1,uid2,uid3',
            'X-Request-Application': 'app_name=android',
            'X-YaTaxi-PhoneId': '590c39bcaa7f19871a38ee91',
            'X-Ya-User-Ticket': 'user_ticket_777',
            'X-Request-Language': 'ru',
        },
        json={
            'services': {
                'taxi': {'image_tags': {'skin_version': '6'}},
                'market_locals': {},
            },
            'range': {
                'older_than': {
                    'market_locals': {
                        'created_at': 1624986307,
                        'created_at_us': 1624986307325000,
                        'order_id': '777',
                    },
                },
                'results': 20,
            },
            'include_service_metadata': True,
        },
    )

    assert response.status == 200
    assert _handler.times_called == market_locals_calls_count
    if market_locals_calls_count == 1:
        assert await response.json() == load_json(
            'expected_resp_market_locals.json',
        )


@pytest.mark.config(
    ORDERHISTORY_SERVICE_IMAGE_TAGS=DEFAULT_IMAGE_TAGS,
    SHUTTLE_ORDERHISTORY_ENABLED=True,
)
@pytest.mark.parametrize(
    'phone_id',
    [
        pytest.param(None, id='no phone_id => no orders'),
        pytest.param(DEFAULT_PHONE_ID, id='yes phone_id => yes orders'),
    ],
)
async def test_no_phone_id(
        mockserver,
        web_app_client,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        phone_id,
        load_json,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_size_hint.json',
            'ridehistory_resp_simple.json',
        )

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'eats_oh_expected_req_simple.json',
            'eats_oh_resp_simple.json',
        )

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/booking/history/list',
    )
    async def handler_shuttle_control(request):
        return load_json('shuttle_control_resp.json')

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers=get_default_headers(phone_id=phone_id),
        json=get_default_response(),
    )

    assert response.status == 200
    data = await response.json()
    if phone_id is not None:
        assert data == load_json('expected_resp_simple.json')
    else:
        assert data == {
            'orders': [],
            'cursor': {},
            'fallback_services': [],
            'error_services': [],
            'service_image_tags': DEFAULT_IMAGE_TAGS,
        }


@pytest.mark.config(
    ORDERHISTORY_SERVICE_IMAGE_TAGS={
        '__default__': 'test',
        'first': 'first_image_tag',
        'second': 'second_image_tag',
    },
    SHUTTLE_ORDERHISTORY_ENABLED=True,
    EATS_ORDERHISTORY_ENABLED=True,
)
async def test_ignore_source_by_exp(
        patch,
        mockserver,
        web_app_client,
        mock_ridehistory,
        mock_eats_orderhistory_py3,
        load_json,
):
    @mock_ridehistory('/v2/list')
    async def handler_taxi(request):
        return _default_handle_ridehistory(
            request,
            load_json,
            'ridehistory_expected_req_size_hint.json',
            'ridehistory_resp_simple.json',
        )

    @mock_eats_orderhistory_py3('/internal-api/v1/orders/retrieve')
    async def handler_eats(request):
        return _default_handle_eats_oh(
            request,
            load_json,
            'eats_oh_expected_req_simple.json',
            'eats_oh_resp_simple.json',
        )

    @mockserver.json_handler(
        '/shuttle-control/internal/shuttle-control/v1/booking/history/list',
    )
    async def handler_shuttle_control(request):
        return load_json('shuttle_control_resp.json')

    @patch('taxi.clients.experiments3.Experiments3Client.get_values')
    async def _mock_get_values(*args, **kwargs):
        return [
            experiments3.ExperimentsValue(
                name=experiments.EXP3_ORDERHISTORY_SOURCES_VISIBILITY,
                value={'enabled': True, 'sources': common.Service.TAXI},
            ),
        ]

    response = await web_app_client.post(
        '/4.0/orderhistory/v2/list',
        headers=get_default_headers(),
        json=get_default_response(),
    )

    assert handler_taxi.times_called == 1
    assert handler_shuttle_control.times_called == 0
    assert handler_eats.times_called == 0

    assert response.status == 200
    assert await response.json() == load_json(
        'expected_resp_ignore_source_by_exp.json',
    )

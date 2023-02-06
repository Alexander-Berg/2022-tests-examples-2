# pylint: disable=W0612,C0103
import json
import uuid

import pytest

CUSTOMER_ID_HASH = uuid.uuid4().hex


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_PARSER_SETTINGS={
        'enable_slots_for_lenta': True,
        'group_id_slots_for_lenta': '123',
    },
)
@pytest.mark.pgsql(
    'eats_retail_retail_parser', files=['add_retail_info_data.sql'],
)
async def test_get_slots_cash_auth(
        web_app_client, taxi_config, web_context, mockserver, load_json,
):
    @mockserver.handler(f'/store/delivery')
    def mock_data_request(request):
        return mockserver.make_response(
            json.dumps(load_json('data_request.json')), 200,
        )

    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    await web_app_client.post(
        '/api/v1/partner/get-picking-slots',
        json={'place_origin_id': uuid.uuid4().hex},
    )
    await web_app_client.post(
        '/api/v1/partner/get-picking-slots',
        json={'place_origin_id': uuid.uuid4().hex},
    )
    assert get_test_get_token.times_called == 1


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_PARSER_SETTINGS={
        'enable_slots_for_lenta': True,
        'enable_new_feature_for_lenta': True,
        'group_id_slots_for_lenta': '123',
    },
)
@pytest.mark.parametrize(
    'request_data, code',
    [
        ({'place_origin_id': uuid.uuid4().hex}, 200),
        (
            {
                'place_origin_id': uuid.uuid4().hex,
                'customer_id_hash': CUSTOMER_ID_HASH,
                'items': [
                    {'origin_id': '123', 'quantity': 2.0},
                    {'origin_id': '322', 'quantity': 3.0},
                ],
            },
            200,
        ),
        ({'place_origin_id': uuid.uuid4().hex}, 500),
    ],
)
@pytest.mark.pgsql(
    'eats_retail_retail_parser', files=['add_retail_info_data.sql'],
)
async def test_get_slots_lenta(
        web_app_client,
        taxi_config,
        web_context,
        mockserver,
        load_json,
        request_data,
        code,
):
    @mockserver.handler(f'/store/delivery')
    def mock_data_request(request):
        if 'customer_id_hash' in request_data:
            assert request.headers['X-Session-Id'] == CUSTOMER_ID_HASH
        return mockserver.make_response(
            json.dumps(load_json('data_request.json')), code,
        )

    @mockserver.handler(f'/order/get-time-slots')
    def mock_get_items(request):
        if 'customer_id_hash' in request_data:
            assert request.headers['X-Session-Id'] == CUSTOMER_ID_HASH
        return mockserver.make_response(
            json.dumps(load_json('data_request.json')), 200,
        )

    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    response = await web_app_client.post(
        '/api/v1/partner/get-picking-slots', json=request_data,
    )
    data = await response.json()
    assert response.status == code
    if code == 200:
        assert load_json('result.json') == data


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_PARSER_SETTINGS={
        'enable_slots_for_lenta': False,
        'group_id_slots_for_lenta': '123',
        'temp_slots_for_lenta': [
            {
                'slot_id': 'slot-id--1h',
                'duration': 1800,
                'from': '2021-11-01T08:30:00',
                'to': '2021-11-01T09:30:00',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'request_data, code', [({'place_origin_id': uuid.uuid4().hex}, 200)],
)
async def test_get_slots_lenta_unenable(
        web_app_client,
        taxi_config,
        web_context,
        mockserver,
        load_json,
        request_data,
        code,
):
    response = await web_app_client.post(
        '/api/v1/partner/get-picking-slots', json=request_data,
    )
    assert response.status == code
    data = await response.json()
    assert data == load_json('result_temp.json')

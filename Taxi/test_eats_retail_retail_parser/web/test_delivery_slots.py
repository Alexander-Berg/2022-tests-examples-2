# pylint: disable=W0612,C0103
import json

import pytest


@pytest.mark.pgsql('eats_retail_retail_parser', files=['add_data.sql'])
@pytest.mark.parametrize(
    'epgr_file_name, slots_file_name, response_status, partner_status',
    [
        ('parser_info.json', 'slots.json', 200, 200),
        ('parser_info.json', 'empty_slots.json', 404, 200),
        ('wrong_parser_info.json', 'slots.json', 400, 200),
        ('parser_info.json', 'slots.json', 400, 400),
    ],
)
async def test_get_slots(
        web_app_client,
        taxi_config,
        web_context,
        mockserver,
        load_json,
        mock_eats_place_groups_replica,
        epgr_file_name,
        slots_file_name,
        response_status,
        partner_status,
):
    @mock_eats_place_groups_replica('/v1/parser_info')
    def _request(request):
        return load_json(epgr_file_name)

    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    @mockserver.handler('/shops/123/delivery_times')
    def get_test_get_slots(request):
        return mockserver.make_response(
            json.dumps(load_json(slots_file_name)), partner_status,
        )

    response = await web_app_client.post(
        '/api/v1/partner/get-delivery-slots',
        json={
            'place_id': 1,
            'place_origin_id': '123',
            'delivery_point': {'latitude': 90, 'longitude': 180},
        },
    )
    assert response.status == response_status
    if response.status == 200:
        data = await response.json()
        row = data['slots']
        parser_info = load_json(epgr_file_name)
        assert row['place_origin_id'] == parser_info['external_id']
        assert row['place_id'] == int(parser_info['place_id'])
        slots_json = load_json(slots_file_name)
        assert len(row['slots']) == len(slots_json['delivery_times'])


@pytest.mark.config(
    EATS_RETAIL_RETAIL_PARSER_PARTNERS_SLOTS_SETTINGS={
        'enable_default_slots': True,
        'default_slots': [
            {
                'from': '1937-01-01T12:00:27.870000+00:20',
                'to': '1937-01-01T12:00:27.870000+00:20',
                'delivery_cost': '123.1',
            },
        ],
    },
)
async def test_get_default_slots(
        web_app_client,
        taxi_config,
        web_context,
        mockserver,
        load_json,
        mock_eats_place_groups_replica,
):
    @mockserver.handler('/security/oauth/token')
    def get_test_get_token(request):
        return mockserver.make_response(
            json.dumps(load_json('test_token.json')), 200,
        )

    response = await web_app_client.post(
        '/api/v1/partner/get-delivery-slots',
        json={
            'place_id': 1,
            'place_origin_id': '123',
            'delivery_point': {'latitude': 90, 'longitude': 180},
        },
    )
    assert response.status == 200
    assert not get_test_get_token.has_calls

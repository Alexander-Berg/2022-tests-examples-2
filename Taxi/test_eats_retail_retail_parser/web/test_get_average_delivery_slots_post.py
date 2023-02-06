# pylint: disable=W0612,C0103
import uuid

import pytest

CUSTOMER_ID_HASH = uuid.uuid4().hex


@pytest.mark.config(EATS_RETAIL_RETAIL_PARSER_PARTNERS_SLOTS_SETTINGS={})
@pytest.mark.pgsql('eats_retail_retail_parser', files=['add_slots_data.sql'])
@pytest.mark.parametrize(
    'file_name, response_status',
    [
        ('place_item.json', 200),
        ('place_items.json', 200),
        ('place_items_without.json', 404),
    ],
)
async def test_get_slots(
        web_app_client,
        taxi_config,
        web_context,
        mockserver,
        load_json,
        mock_eats_place_groups_replica,
        file_name,
        response_status,
):
    @mock_eats_place_groups_replica('/v1/parser_infos')
    def _request(request):
        return {'items': load_json(file_name), 'meta': {}}

    response = await web_app_client.post(
        '/api/v1/partner/get-average-delivery-slots',
        json={'places': [{'place_origin_id': 'external_id2', 'place_id': 2}]},
    )
    assert response.status == response_status
    if response.status == 200:
        data = await response.json()
        assert len(data['slots_by_place']) == len(load_json(file_name))


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
    @mock_eats_place_groups_replica('/v1/parser_infos')
    def _request(request):
        return {}

    response = await web_app_client.post(
        '/api/v1/partner/get-average-delivery-slots',
        json={'places': [{'place_origin_id': 'external_id2', 'place_id': 2}]},
    )
    assert response.status == 200
    assert not _request.has_calls

import pytest

HANDLER = '/v1/manage/sku/info'


@pytest.mark.config(
    EATS_NOMENCLATURE_HANDLER_LIMIT_ITEMS={
        'api_v1_manage_sku_info_post': {'max_items_count': 10},
    },
)
@pytest.mark.pgsql('eats_nomenclature', files=['fill_sku.sql'])
async def test_response(taxi_eats_nomenclature):
    brand_id = 1
    request_sku_ids = [
        'unknown_sku_uuid',
        'sku_uuid_1',
        'sku_uuid_2',
        'sku_uuid_3',
    ]
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'brand_id': brand_id, 'sku_ids': request_sku_ids},
    )
    assert response.status_code == 200

    expected_sku_info = [
        {
            'id': 'sku_uuid_1',
            'name': 'sku_name_1',
            'weight': '100 г',
            'volume': '100 мл',
            'picture_url': 'picture_url_1',
        },
        {
            'id': 'sku_uuid_2',
            'name': 'sku_name_2',
            'weight': '200 г',
            'picture_url': 'picture_url_2',
        },
        {'id': 'sku_uuid_3', 'name': 'sku_name_3'},
    ]

    assert _sorted(response.json()['sku_info']) == _sorted(expected_sku_info)


@pytest.mark.pgsql('eats_nomenclature', files=['fill_sku.sql'])
async def test_requested_items_limit(taxi_eats_nomenclature, taxi_config):
    taxi_config.set_values(
        {
            'EATS_NOMENCLATURE_HANDLER_LIMIT_ITEMS': {
                'api_v1_manage_sku_info_post': {'max_items_count': 3},
            },
        },
    )

    brand_id = 1
    request_sku_ids = ['sku_uuid_1', 'sku_uuid_2', 'sku_uuid_3', 'sku_uuid_4']
    response = await taxi_eats_nomenclature.post(
        HANDLER, json={'brand_id': brand_id, 'sku_ids': request_sku_ids},
    )
    assert response.status_code == 400


def _sorted(data):
    return sorted(data, key=lambda item: item['id'])

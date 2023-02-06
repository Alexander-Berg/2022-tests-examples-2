import pytest

from ... import utils

PLACE_ID = 1
HANDLER = '/v1/place/products/search-by-barcode-or-vendor-code'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_404_unknown_place_id(
        taxi_eats_nomenclature, mock_core_max_overweight,
):
    unknown_place_id = 123456
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={unknown_place_id}',
        json=_generate_request_json(
            [{'vendor_code': 'smth', 'barcode': 'smth'}],
        ),
    )
    assert response.status == 404


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_400_empty(taxi_eats_nomenclature, mock_core_max_overweight):
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}', json=_generate_request_json([]),
    )
    assert response.status == 400


@pytest.mark.config(
    EATS_NOMENCLATURE_HANDLER_LIMIT_ITEMS={
        '/v1/place/products/search-by-barcode-or-vendor-code_POST': {
            'max_items_count': 1,
        },
    },
)
@pytest.mark.parametrize(
    **utils.gen_list_params('max_items_count', values=[2, 5]),
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_400_too_many(
        taxi_eats_nomenclature,
        mock_core_max_overweight,
        update_taxi_config,
        # parametrize
        max_items_count,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_HANDLER_LIMIT_ITEMS',
        {
            '/v1/place/products/search-by-barcode-or-vendor-code_POST': {
                'max_items_count': max_items_count,
            },
        },
    )

    data = []
    for i in range(0, max_items_count + 1):
        data.append({'vendor_code': str(i), 'barcode': str(i)})

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}', json=_generate_request_json(data),
    )
    assert response.status == 400

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID}',
        json=_generate_request_json(data[:-1]),
    )
    assert response.status == 200


def _generate_request_json(data):
    return {
        'items': [
            {'vendor_code': i['vendor_code'], 'barcode': i['barcode']}
            for i in data
        ],
    }

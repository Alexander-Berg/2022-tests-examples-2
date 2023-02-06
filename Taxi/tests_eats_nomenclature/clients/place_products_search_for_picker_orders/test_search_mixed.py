import pytest

BRAND_ID = 1
PLACE_ID = 1
HANDLER = '/v1/place/products/search-by-barcode-or-vendor-code'


@pytest.mark.parametrize(
    'db_data,handler_data',
    [
        pytest.param(
            [{'barcode': '1', 'vendor_code': '1'}],
            [
                {
                    'requested_barcode': '2',
                    'requested_vendor_code': '1',
                    'expected_barcode': '1',
                    'expected_vendor_code': '1',
                },
            ],
            id='vendor code over barcode',
        ),
        pytest.param(
            [{'barcode': '1', 'vendor_code': '1'}],
            [
                {
                    'requested_barcode': '1',
                    'requested_vendor_code': '2',
                    'expected_barcode': '1',
                    'expected_vendor_code': '1',
                },
            ],
            id='barcode over vendor code',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_200(
        taxi_eats_nomenclature,
        mock_core_max_overweight,
        sql_add_product_for_vendor_and_barcode_test,
        # parametrize
        db_data,
        handler_data,
):
    place_id = PLACE_ID

    for i in db_data:
        sql_add_product_for_vendor_and_barcode_test(
            place_id=PLACE_ID,
            vendor_code=i['vendor_code'],
            barcode=i['barcode'],
        )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json=_generate_request_json(handler_data),
    )
    assert response.status_code == 200
    _verify_response(response.json(), handler_data)


def _generate_request_json(data):
    return {
        'items': [
            {
                'barcode': i['requested_barcode'],
                'vendor_code': i['requested_vendor_code'],
            }
            for i in data
        ],
    }


def _verify_response(response, handler_data):
    response_items = {
        **{
            f'{i["barcode"]}|{i["vendor_code"]}': {
                'barcode': i['item']['barcode']['values'][0],
                'vendor_code': i['item']['vendor_code'],
            }
            for i in response['matched_items']
        },
        **{
            f'{i["barcode"]}|{i["vendor_code"]}': {
                'barcode': None,
                'vendor_code': None,
            }
            for i in response['not_matched_items']
        },
    }
    expected_items = {
        f'{i["requested_barcode"]}|{i["requested_vendor_code"]}': {
            'barcode': i['expected_barcode'],
            'vendor_code': i['expected_vendor_code'],
        }
        for i in handler_data
    }

    assert response_items == expected_items

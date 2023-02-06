import pytest

PLACE_ID_1 = 1
PLACE_ID_2 = 2
HANDLER = '/v1/place/products/search-by-barcode-or-vendor-code'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_200(
        taxi_eats_nomenclature,
        mock_core_max_overweight,
        sql_add_product_for_vendor_and_barcode_test,
):
    place_id = PLACE_ID_1
    db_vendor_codes = ['1', '2', '3']
    unknown_vendor_codes = ['unknown_1', 'unknown_2']

    requested_vendor_codes = db_vendor_codes + unknown_vendor_codes

    for i in db_vendor_codes:
        sql_add_product_for_vendor_and_barcode_test(
            place_id=PLACE_ID_1, vendor_code=i,
        )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json=_generate_request_json(requested_vendor_codes),
    )
    assert response.status_code == 200
    _verify_response(
        response.json(),
        matched_vendor_codes=db_vendor_codes,
        not_matched_vendor_codes=unknown_vendor_codes,
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_product_in_different_places(
        taxi_eats_nomenclature,
        mock_core_max_overweight,
        sql_add_product_for_vendor_and_barcode_test,
):
    place_1_vendor_code = '1'
    place_2_vendor_code = '2'

    requested_vendor_codes = place_1_vendor_code + place_2_vendor_code

    sql_add_product_for_vendor_and_barcode_test(
        place_id=PLACE_ID_1, vendor_code=place_1_vendor_code,
    )
    sql_add_product_for_vendor_and_barcode_test(
        place_id=PLACE_ID_2, vendor_code=place_2_vendor_code,
    )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID_1}',
        json=_generate_request_json(requested_vendor_codes),
    )
    assert response.status_code == 200
    _verify_response(
        response.json(),
        matched_vendor_codes=[place_1_vendor_code],
        not_matched_vendor_codes=[place_2_vendor_code],
    )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID_2}',
        json=_generate_request_json(requested_vendor_codes),
    )
    assert response.status_code == 200
    _verify_response(
        response.json(),
        matched_vendor_codes=[place_2_vendor_code],
        not_matched_vendor_codes=[place_1_vendor_code],
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_multiple_product_match(
        taxi_eats_nomenclature,
        mock_core_max_overweight,
        update_taxi_config,
        sql_add_product_for_vendor_and_barcode_test,
):
    place_id = PLACE_ID_1

    sql_add_product_for_vendor_and_barcode_test(
        place_id=place_id, vendor_code='aaaaa', origin_id='1',
    )
    sql_add_product_for_vendor_and_barcode_test(
        place_id=place_id, vendor_code='aaaaa', origin_id='2',
    )

    expected_origin_ids = {'1', '2'}

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json=_generate_request_json(['aaaaa']),
    )
    assert response.status_code == 200
    response_json = response.json()
    assert {
        i['item']['origin_id'] for i in response_json['matched_items']
    } == expected_origin_ids
    assert response_json['not_matched_items'] == []


def _generate_request_json(vendor_codes):
    return {
        'items': [{'vendor_code': i, 'barcode': None} for i in vendor_codes],
    }


def _verify_response(response, matched_vendor_codes, not_matched_vendor_codes):
    assert {
        i['item']['vendor_code'] for i in response['matched_items']
    } == set(matched_vendor_codes)
    assert {i['vendor_code'] for i in response['matched_items']} == set(
        matched_vendor_codes,
    )
    assert {i['vendor_code'] for i in response['not_matched_items']} == set(
        not_matched_vendor_codes,
    )

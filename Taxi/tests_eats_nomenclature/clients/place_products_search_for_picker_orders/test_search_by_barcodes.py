import pytest

from ... import utils

BRAND_ID = 1
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
    db_barcodes = ['1', '2', '3']
    unknown_barcodes = ['unknown_1', 'unknown_2']
    barcode_to_matched_value = {
        **{i: i for i in db_barcodes},
        **{i: None for i in unknown_barcodes},
    }

    requested_barcodes = db_barcodes + unknown_barcodes

    for i in db_barcodes:
        sql_add_product_for_vendor_and_barcode_test(
            place_id=PLACE_ID_1, barcode=i,
        )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json=_generate_request_json(requested_barcodes),
    )
    assert response.status_code == 200
    _verify_response(response.json(), barcode_to_matched_value)


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_product_in_different_places(
        taxi_eats_nomenclature,
        mock_core_max_overweight,
        sql_add_product_for_vendor_and_barcode_test,
):
    place_1_barcode = '1'
    place_2_barcode = '2'

    requested_barcodes = place_1_barcode + place_2_barcode

    sql_add_product_for_vendor_and_barcode_test(
        place_id=PLACE_ID_1, barcode=place_1_barcode,
    )
    sql_add_product_for_vendor_and_barcode_test(
        place_id=PLACE_ID_2, barcode=place_2_barcode,
    )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID_1}',
        json=_generate_request_json(requested_barcodes),
    )
    assert response.status_code == 200
    _verify_response(
        response.json(),
        {place_1_barcode: place_1_barcode, place_2_barcode: None},
    )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={PLACE_ID_2}',
        json=_generate_request_json(requested_barcodes),
    )
    assert response.status_code == 200
    _verify_response(
        response.json(),
        {place_2_barcode: place_2_barcode, place_1_barcode: None},
    )


@pytest.mark.parametrize(**utils.gen_bool_params('enable_fuzzy_search'))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_fuzzy_search_enabled(
        taxi_eats_nomenclature,
        mock_core_max_overweight,
        update_taxi_config,
        sql_add_product_for_vendor_and_barcode_test,
        # parametrize
        enable_fuzzy_search,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_PRODUCTS_SEARCH_BY_BARCODE',
        {
            'per_brand_search_settings': {
                BRAND_ID: {
                    'fuzzy_search_enabled': enable_fuzzy_search,
                    'min_barcode_length': 3,
                },
            },
        },
    )

    place_id = PLACE_ID_1

    db_barcodes = ['aaaaa', 'bbbb']
    requested_barcodes = ['aaaaa', 'bbbbb']
    barcode_to_matched_value = {
        'aaaaa': 'aaaaa',
        'bbbbb': 'bbbb' if enable_fuzzy_search else None,
    }

    for i in db_barcodes:
        sql_add_product_for_vendor_and_barcode_test(
            place_id=PLACE_ID_1, barcode=i,
        )

    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json=_generate_request_json(requested_barcodes),
    )
    assert response.status_code == 200
    _verify_response(response.json(), barcode_to_matched_value)


@pytest.mark.parametrize(**utils.gen_bool_params('enable_fuzzy_search'))
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_multiple_product_match(
        taxi_eats_nomenclature,
        mock_core_max_overweight,
        update_taxi_config,
        sql_add_product_for_vendor_and_barcode_test,
        # parametrize
        enable_fuzzy_search,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_PRODUCTS_SEARCH_BY_BARCODE',
        {
            'per_brand_search_settings': {
                BRAND_ID: {
                    'fuzzy_search_enabled': enable_fuzzy_search,
                    'min_barcode_length': 3,
                },
            },
        },
    )

    place_id = PLACE_ID_1

    sql_add_product_for_vendor_and_barcode_test(
        place_id=place_id, barcode='aaaaa', origin_id='1',
    )
    sql_add_product_for_vendor_and_barcode_test(
        place_id=place_id, barcode='aaaaa', origin_id='2',
    )
    sql_add_product_for_vendor_and_barcode_test(
        place_id=place_id, barcode='aaaa', origin_id='3',
    )

    expected_origin_ids = {'1', '2'}
    if enable_fuzzy_search:
        expected_origin_ids.add('3')

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


@pytest.mark.parametrize(
    'min_barcode_length,db_barcodes,barcode_to_matched_value',
    [
        pytest.param(
            2,
            ['aaaaa', 'bbbb', 'ccc', 'dd', 'e'],
            {
                'aaaaa': 'aaaaa',
                'bbbbb': 'bbbb',
                'ccccc': 'ccc',
                'ddddd': 'dd',
                'eeeee': None,
            },
            id='cropped(2)',
        ),
        pytest.param(
            3,
            ['aaaaa', 'bbbb', 'ccc', 'dd', 'e'],
            {
                'aaaaa': 'aaaaa',
                'bbbbb': 'bbbb',
                'ccccc': 'ccc',
                'ddddd': None,
                'eeeee': None,
            },
            id='cropped(3)',
        ),
        pytest.param(
            2,
            ['aaaaa', 'bbbb0', 'ccc00', 'dd000', 'e0000'],
            {
                'aaaaa': 'aaaaa',
                'bbbbb': 'bbbb0',
                'ccccc': 'ccc00',
                'ddddd': 'dd000',
                'eeeee': None,
            },
            id='padded(2)',
        ),
        pytest.param(
            3,
            ['aaaaa', 'bbbb0', 'ccc00', 'dd000', 'e0000'],
            {
                'aaaaa': 'aaaaa',
                'bbbbb': 'bbbb0',
                'ccccc': 'ccc00',
                'ddddd': None,
                'eeeee': None,
            },
            id='padded(3)',
        ),
        pytest.param(
            2,
            ['aaaaa', 'bbb0b', 'cc00c', 'd000d'],
            {
                'aaaaa': 'aaaaa',
                'bbbbb': 'bbb0b',
                'ccccc': 'cc00c',
                'ddddd': None,
            },
            id='partially padded(2)',
        ),
        pytest.param(
            3,
            ['aaaaa', 'bbb0b', 'cc00c', 'd000d'],
            {'aaaaa': 'aaaaa', 'bbbbb': 'bbb0b', 'ccccc': None, 'ddddd': None},
            id='partially padded(3)',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_fuzzy_search_algorithm(
        taxi_eats_nomenclature,
        mock_core_max_overweight,
        update_taxi_config,
        sql_add_product_for_vendor_and_barcode_test,
        # parametrize
        min_barcode_length,
        db_barcodes,
        barcode_to_matched_value,
):
    update_taxi_config(
        'EATS_NOMENCLATURE_PRODUCTS_SEARCH_BY_BARCODE',
        {
            'per_brand_search_settings': {
                BRAND_ID: {
                    'fuzzy_search_enabled': True,
                    'min_barcode_length': min_barcode_length,
                },
            },
        },
    )

    place_id = PLACE_ID_1

    for i in db_barcodes:
        sql_add_product_for_vendor_and_barcode_test(
            place_id=PLACE_ID_1, barcode=i,
        )

    requested_barcodes = barcode_to_matched_value.keys()
    response = await taxi_eats_nomenclature.post(
        f'{HANDLER}?place_id={place_id}',
        json=_generate_request_json(requested_barcodes),
    )
    assert response.status_code == 200
    _verify_response(response.json(), barcode_to_matched_value)


def _generate_request_json(barcodes):
    return {'items': [{'vendor_code': None, 'barcode': i} for i in barcodes]}


def _verify_response(response, expected_barcode_to_matched_value):
    barcode_to_matched_value = {
        **{
            i['barcode']: i['item']['barcode']['values'][0]
            for i in response['matched_items']
        },
        **{i['barcode']: None for i in response['not_matched_items']},
    }

    assert barcode_to_matched_value == expected_barcode_to_matched_value

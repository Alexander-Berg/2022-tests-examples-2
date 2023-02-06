import copy

import pytest

from tests_eats_retail_market_integration import models


CORE_HANDLER = '/eats-core-retail/v1/place/additional-info/retrieve'
PLACE_ID = '1'
BRAND_ID = '111'
PARTNER_ID = 10
BUSINESS_ID = 100
FEED_ID = 1000


async def test_place_info_updater(
        get_places_info_from_db,
        mockserver,
        save_brands_to_db,
        save_market_brand_places_to_db,
        stq_runner,
):
    [brands, market_brand_places] = _generate_db_init_data()
    save_brands_to_db(brands)
    save_market_brand_places_to_db(market_brand_places)

    # Check place_info insert.
    expected_place_info_args = {
        'place_id': PLACE_ID,
        'partner_id': PARTNER_ID,
        'brand_name': 'some_brand_name_1',
        'place_name': 'some_place_name_1',
        'legal_name': 'some_legal_name_1',
        'legal_address': 'some_legal_address_1',
        'legal_address_postcode': 'some_legal_address_postcode_1',
        'reg_number': 'some_reg_number_1',
        'email': 'some_email_1',
        'address_full': 'some_address_full_1',
        'phone': 'some_phone_1',
        'inn': 'some_inn_1',
        'kpp': 'some_kpp_1',
        'geo_id': 123,
        'schedule': [
            {'weekday': 'monday', 'from': '12:00', 'duration': 10},
            {'weekday': 'sunday', 'from': '10:00'},
        ],
        'assembly_cost': None,
        'brand_id': BRAND_ID,
    }
    expected_place_info = [models.PlaceInfo(**expected_place_info_args)]

    @mockserver.json_handler(CORE_HANDLER)
    def _mock_eats_core_retail_place_info(request):
        assert request.json['place_id'] == PLACE_ID
        response = copy.deepcopy(expected_place_info_args)
        del response['place_id']
        del response['partner_id']
        return response

    await stq_runner.eats_retail_market_integration_update_places_info.call(
        task_id=PLACE_ID,
        args=[],
        kwargs={'place_id': PLACE_ID},
        expect_fail=False,
    )

    assert get_places_info_from_db() == expected_place_info

    # Check place_info update.
    expected_place_info_args = {
        'place_id': PLACE_ID,
        'partner_id': PARTNER_ID,
        'brand_name': None,
        'place_name': 'some_place_name_2',
        'legal_name': 'some_legal_name_2',
        'legal_address': None,
        'legal_address_postcode': 'some_legal_address_postcode_2',
        'reg_number': None,
        'email': 'some_email_2',
        'address_full': None,
        'phone': 'some_phone_2',
        'inn': 'some_inn_2',
        'kpp': None,
        'geo_id': 456,
        'schedule': None,
        'assembly_cost': 1,
        'brand_id': BRAND_ID,
    }

    expected_updated_place_info = [
        models.PlaceInfo(**expected_place_info_args),
    ]

    await stq_runner.eats_retail_market_integration_update_places_info.call(
        task_id=PLACE_ID,
        args=[],
        kwargs={'place_id': PLACE_ID},
        expect_fail=False,
    )

    assert get_places_info_from_db() == expected_updated_place_info


@pytest.mark.parametrize('core_response_code', ['500', '404'])
async def test_core_error(
        get_places_info_from_db,
        mockserver,
        pg_realdict_cursor,
        save_brands_to_db,
        save_market_brand_places_to_db,
        stq_runner,
        core_response_code,
):
    [brands, market_brand_places] = _generate_db_init_data()
    save_brands_to_db(brands)
    save_market_brand_places_to_db(market_brand_places)

    @mockserver.json_handler(CORE_HANDLER)
    def _mock_eats_core_retail_place_info(request):
        return mockserver.make_response(core_response_code)

    old_places_info = get_places_info_from_db()

    await stq_runner.eats_retail_market_integration_update_places_info.call(
        task_id=PLACE_ID,
        args=[],
        kwargs={'place_id': PLACE_ID},
        expect_fail=False,
    )

    assert get_places_info_from_db() == old_places_info


async def test_stq_error_limit(
        mockserver, stq_runner, testpoint, update_taxi_config,
):
    max_retries_on_error = 3
    update_taxi_config(
        'EATS_RETAIL_MARKET_INTEGRATION_STQ_PROCESSING',
        {
            'stq_update_places_info': {
                'max_retries_on_error': max_retries_on_error,
            },
        },
    )

    @mockserver.json_handler(CORE_HANDLER)
    def _mock_eats_core_retail_place_info(request):
        return {'place_name': 'some_place_name'}

    @testpoint('eats-retail-market-integration-update-places-info::fail')
    def _task_testpoint(param):
        return {'inject_failure': True}

    for i in range(max_retries_on_error):
        await stq_runner.eats_retail_market_integration_update_places_info.call(  # noqa: E501 pylint: disable=line-too-long
            task_id='1',
            args=[],
            kwargs={'place_id': '1'},
            expect_fail=True,
            exec_tries=i,
        )

    # should succeed because of the error limit
    await stq_runner.eats_retail_market_integration_update_places_info.call(
        task_id='1',
        args=[],
        kwargs={'place_id': '1'},
        expect_fail=False,
        exec_tries=max_retries_on_error,
    )


def _generate_db_init_data():
    brand1 = models.Brand(brand_id=BRAND_ID, slug=BRAND_ID)
    brand1.add_places([models.Place(place_id=PLACE_ID, slug=PLACE_ID)])
    brands = [brand1]

    market_brand_places = [
        models.MarketBrandPlace(
            brand_id=BRAND_ID,
            place_id=PLACE_ID,
            business_id=BUSINESS_ID,
            partner_id=PARTNER_ID,
            feed_id=FEED_ID,
        ),
    ]
    return [brands, market_brand_places]

import pytest

TASK_NAME = 'periodic-mapping'
EATS_URL = (
    '/eats-catalog-storage'
    + '/internal/eats-catalog-storage/v1/delivery_zones/retrieve-by-place-ids'
)

EATS_MARKET_DSBS_PLACE_TO_MARKET_EXAMPLE = {'111': {'partner_id': '1'}}
EATS_MARKET_DSBS_PLACE_TO_MARKET_MEXAMPLE = {
    '222': {'partner_id': '2'},
    '111': {'partner_id': '1'},
}
EATS_MARKET_DSBS_PERIODIC_PERIOD_EXAMPLE = {'task_period_seconds': 600}


@pytest.mark.config(
    EATS_MARKET_DSBS_PLACE_TO_MARKET=EATS_MARKET_DSBS_PLACE_TO_MARKET_EXAMPLE,
    EATS_MARKET_DSBS_PERIODIC_PERIOD=EATS_MARKET_DSBS_PERIODIC_PERIOD_EXAMPLE,
    EATS_MARKET_DSBS_ZONES_MAPPING_ENABLED={'is_zones_mapping_enabled': True},
)
async def test_zone_mapping(
        taxi_eats_market_dsbs, mockserver, load_json, taxi_config,
):
    @mockserver.json_handler(EATS_URL)
    def _handler_eats_catalog_storage(request):
        # need to check containing name, polygon and enabled
        assert 'polygon' in request.json['projection']
        assert 'name' in request.json['projection']
        assert 'enabled' in request.json['projection']
        mock_response = load_json('full_response.json')
        return mockserver.make_response(json=mock_response, status=200)

    partner_id = taxi_config.get('EATS_MARKET_DSBS_PLACE_TO_MARKET')[
        '111'
    ].get('partner_id')
    market_url = f'/market-nesu/internal/partner/{partner_id}/polygonal-zones'

    @mockserver.json_handler(market_url)
    def _handler_market_nesu(request):
        current_request = request.json
        assert len(current_request) == 1
        current_object = current_request['zones'][0]['geo']
        expected_object = load_json('expected_request_to_market.json')[
            'zones'
        ][0]['geo']
        assert current_object['type'] == expected_object['type']
        assert current_object['enabled'] == expected_object['enabled']
        assert current_object['id'] == expected_object['id']
        assert current_object['name'] == expected_object['name']
        assert current_object['coordinates'] == expected_object['coordinates']
        return mockserver.make_response(
            headers={'x-market-req-id': '123'}, status=200,
        )

    await taxi_eats_market_dsbs.run_distlock_task(TASK_NAME)

    assert _handler_eats_catalog_storage.times_called == 1
    assert _handler_market_nesu.times_called == 1


@pytest.mark.config(
    EATS_MARKET_DSBS_PLACE_TO_MARKET=EATS_MARKET_DSBS_PLACE_TO_MARKET_MEXAMPLE,
    EATS_MARKET_DSBS_PERIODIC_PERIOD=EATS_MARKET_DSBS_PERIODIC_PERIOD_EXAMPLE,
    EATS_MARKET_DSBS_ZONES_MAPPING_ENABLED={'is_zones_mapping_enabled': True},
)
async def test_zone_mapping_with_first_failed(
        taxi_eats_market_dsbs, mockserver, load_json, taxi_config,
):
    @mockserver.json_handler(EATS_URL)
    def _handler_eats_catalog_storage(request):
        if request.json['place_ids'][0] == 111:
            mock_response = load_json('full_response.json')
        if request.json['place_ids'][0] == 222:
            mock_response = load_json('full_response_222.json')
        return mockserver.make_response(json=mock_response, status=200)

    partner_id_111 = taxi_config.get('EATS_MARKET_DSBS_PLACE_TO_MARKET')[
        '111'
    ].get('partner_id')
    market_url_111 = (
        f'/market-nesu/internal/partner/{partner_id_111}/polygonal-zones'
    )

    partner_id_222 = taxi_config.get('EATS_MARKET_DSBS_PLACE_TO_MARKET')[
        '222'
    ].get('partner_id')
    market_url_222 = (
        f'/market-nesu/internal/partner/{partner_id_222}/polygonal-zones'
    )

    @mockserver.json_handler(market_url_111)
    def _handler_market_nesu_111(request):
        return mockserver.make_response(status=403)

    @mockserver.json_handler(market_url_222)
    def _handler_market_nesu_222(request):
        return mockserver.make_response(
            headers={'x-market-req-id': '123'}, status=200,
        )

    await taxi_eats_market_dsbs.run_distlock_task(TASK_NAME)

    assert _handler_eats_catalog_storage.times_called == 2
    assert _handler_market_nesu_111.times_called == 1
    assert _handler_market_nesu_222.times_called == 1


@pytest.mark.config(
    EATS_MARKET_DSBS_PLACE_TO_MARKET=EATS_MARKET_DSBS_PLACE_TO_MARKET_EXAMPLE,
    EATS_MARKET_DSBS_PERIODIC_PERIOD=EATS_MARKET_DSBS_PERIODIC_PERIOD_EXAMPLE,
    EATS_MARKET_DSBS_ZONES_MAPPING_ENABLED={'is_zones_mapping_enabled': True},
)
async def test_zone_mapping_not_valid_data(
        taxi_eats_market_dsbs, mockserver, load_json,
):
    @mockserver.json_handler(EATS_URL)
    def _handler_eats_catalog_storage(request):
        mock_response = load_json('not_full_response.json')  # enabled deleted
        return mockserver.make_response(json=mock_response, status=200)

    # market-nesu mock should not be called

    await taxi_eats_market_dsbs.run_distlock_task(TASK_NAME)

    assert _handler_eats_catalog_storage.times_called == 1


@pytest.mark.config(
    EATS_MARKET_DSBS_PLACE_TO_MARKET=EATS_MARKET_DSBS_PLACE_TO_MARKET_EXAMPLE,
    EATS_MARKET_DSBS_PERIODIC_PERIOD=EATS_MARKET_DSBS_PERIODIC_PERIOD_EXAMPLE,
    EATS_MARKET_DSBS_ZONES_MAPPING_ENABLED={'is_zones_mapping_enabled': True},
)
async def test_zone_mapping_not_exist_place_id(
        taxi_eats_market_dsbs, mockserver, load_json,
):
    @mockserver.json_handler(EATS_URL)
    def _handler_eats_catalog_storage(request):
        mock_response = load_json('not_exist_place_id_response.json')
        return mockserver.make_response(json=mock_response, status=200)

    # market-nesu mock should not be called

    await taxi_eats_market_dsbs.run_distlock_task(TASK_NAME)

    assert _handler_eats_catalog_storage.times_called == 1


@pytest.mark.config(
    EATS_MARKET_DSBS_ZONES_MAPPING_ENABLED={'is_zones_mapping_enabled': False},
)
async def test_zone_mapping_disabled(taxi_eats_market_dsbs):
    # Mocks should not be called
    await taxi_eats_market_dsbs.run_distlock_task(TASK_NAME)

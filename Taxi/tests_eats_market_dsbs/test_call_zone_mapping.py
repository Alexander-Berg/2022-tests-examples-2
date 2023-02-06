import pytest

EATS_MARKET_DSBS_PLACE_TO_MARKET_EXAMPLE = {'111': {'partner_id': '1'}}
EATS_MARKET_DSBS_PLACE_TO_MARKET_SEXAMPLE = {'abra': {'partner_id': '1'}}

URL = 'internal/eats-market-dsbs/v1/send-zone'


@pytest.mark.config(
    EATS_MARKET_DSBS_PLACE_TO_MARKET=EATS_MARKET_DSBS_PLACE_TO_MARKET_EXAMPLE,
)
async def test_call_zone_mapping_full(
        taxi_eats_market_dsbs,
        mock_eats_catalog_storage_full,
        mock_market_nesu,
):
    query = {'place_id': '111'}
    response = await taxi_eats_market_dsbs.post(URL, params=query)
    assert response.status_code == 200


@pytest.mark.config(
    EATS_MARKET_DSBS_PLACE_TO_MARKET=EATS_MARKET_DSBS_PLACE_TO_MARKET_EXAMPLE,
)
async def test_call_zone_mapping_not_full(
        taxi_eats_market_dsbs, mock_eats_catalog_storage_not_full,
):
    # market-nesu mock should not be called
    query = {'place_id': '111'}
    response = await taxi_eats_market_dsbs.post(URL, params=query)
    assert response.status_code == 200


@pytest.mark.config(
    EATS_MARKET_DSBS_PLACE_TO_MARKET=EATS_MARKET_DSBS_PLACE_TO_MARKET_EXAMPLE,
)
async def test_zone_mapping_not_exist_place_id(
        taxi_eats_market_dsbs, mock_eats_catalog_storage_not_exist,
):
    # market-nesu mock should not be called
    query = {'place_id': '111'}
    response = await taxi_eats_market_dsbs.post(URL, params=query)
    assert response.status_code == 500


@pytest.mark.config(
    EATS_MARKET_DSBS_PLACE_TO_MARKET=EATS_MARKET_DSBS_PLACE_TO_MARKET_SEXAMPLE,
)
async def test_zone_mapping_not_integer_place_id(taxi_eats_market_dsbs):
    # mocks should not be called
    query = {'place_id': 'abra'}
    response = await taxi_eats_market_dsbs.post(URL, params=query)
    assert response.status_code == 400


@pytest.mark.config(
    EATS_MARKET_DSBS_PLACE_TO_MARKET=EATS_MARKET_DSBS_PLACE_TO_MARKET_EXAMPLE,
)
async def test_zone_mapping_not_found_place_id(taxi_eats_market_dsbs):
    # mocks should not be called
    query = {'place_id': '222'}
    response = await taxi_eats_market_dsbs.post(URL, params=query)
    assert response.status_code == 404

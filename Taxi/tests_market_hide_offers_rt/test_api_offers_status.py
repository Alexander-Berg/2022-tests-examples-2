# flake8: noqa
# pylint: disable=import-error,wildcard-import

import os
import pytest
import shutil
import yatest.common

from tests_market_hide_offers_rt import utils

API = '/v1/offers/check_status'


@pytest.fixture()
def teardown():
    yield
    path = yatest.common.work_path() + '/' + utils.DIR
    if os.path.exists(path):
        shutil.rmtree(path)


# Check api offers status with invalid input arguments expect 400
async def test_api_offers_status_with_invalid_arguments(
        taxi_market_hide_offers_rt, teardown,
):
    # Prepare only one hide rule
    await utils.prepare_abo_data(
        [utils.AboRule(utils.ID1, utils.YABS_ID1)], taxi_market_hide_offers_rt,
    )

    response = await taxi_market_hide_offers_rt.post(API, json={'items': [{}]})

    assert response.status_code == 400


# Check api offers status with internal error expect 500
async def test_api_offers_status_with_internal_error(
        taxi_market_hide_offers_rt, teardown,
):
    # There is no test data preparation, so will be an error
    await utils.prepare_test_api(taxi_market_hide_offers_rt, '', '', '')

    request_info = utils.RequestInfo(213, [''])
    business_offer = utils.BusinessOffer(utils.ID1, utils.YABS_ID1, [''])
    service_offers = [utils.ServiceOffer(utils.ID2, [''], '')]

    response = await taxi_market_hide_offers_rt.post(
        API,
        json=utils.prepare_request_data(
            [utils.Request(business_offer, service_offers, request_info)],
        ),
    )

    assert response.status_code == 500


# Check api offers status for unknown offer expect 200 and 'denied'
@pytest.mark.redis_store(
    ['set', utils.REDIS_KEY_1.decode(), utils.REDIS_VALUE_ALLOWED.decode()],
)
async def test_api_offers_status_with_unknown_offer(
        taxi_market_hide_offers_rt, teardown,
):
    await utils.prepare_abo_data(
        [utils.AboRule(utils.ID2, utils.YABS_ID2)], taxi_market_hide_offers_rt,
    )

    request_info = utils.RequestInfo(utils.MOSCOW, [''])
    business_offer = utils.BusinessOffer(utils.ID3, utils.YABS_ID3, [''])
    service_offers = [utils.ServiceOffer(utils.ID3, [''], 'denied')]

    response = await taxi_market_hide_offers_rt.post(
        API,
        json=utils.prepare_request_data(
            [utils.Request(business_offer, service_offers, request_info)],
        ),
    )

    assert response.status_code == 200
    assert response.json() == utils.prepare_response_data(
        [utils.Response(business_offer, service_offers)],
    )

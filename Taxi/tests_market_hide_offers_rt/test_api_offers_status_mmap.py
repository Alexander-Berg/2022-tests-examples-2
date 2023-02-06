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


# Check api offers status for denied offer expect 200 and 'denied'
@pytest.mark.redis_store(
    ['set', utils.REDIS_KEY_1.decode(), utils.REDIS_VALUE_ALLOWED.decode()],
)
async def test_api_offers_status_with_single_hide_status(
        taxi_market_hide_offers_rt, teardown,
):
    await utils.prepare_abo_data(
        [utils.AboRule(utils.ID1, utils.YABS_ID1)], taxi_market_hide_offers_rt,
    )

    request_info = utils.RequestInfo(utils.MOSCOW, [''])
    business_offer = utils.BusinessOffer(utils.ID1, utils.YABS_ID1, [''])
    service_offers = [utils.ServiceOffer(utils.ID1, [''], 'denied')]

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


# Check api offers status for allowed offer expect 200 and 'allowed'
@pytest.mark.redis_store(
    ['set', utils.REDIS_KEY_1.decode(), utils.REDIS_VALUE_ALLOWED.decode()],
)
async def test_api_offers_status_with_single_no_hide_status(
        taxi_market_hide_offers_rt, teardown,
):
    await utils.prepare_abo_data(
        [utils.AboRule(utils.ID2, utils.YABS_ID2)], taxi_market_hide_offers_rt,
    )

    request_info = utils.RequestInfo(utils.MOSCOW, [''])
    business_offer = utils.BusinessOffer(utils.ID1, utils.YABS_ID1, [''])
    service_offers = [utils.ServiceOffer(utils.ID1, [''], 'allowed')]

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


# Check api offers status for multiple denied offers expect 200 and 'denied'
@pytest.mark.redis_store(
    ['set', utils.REDIS_KEY_1.decode(), utils.REDIS_VALUE_ALLOWED.decode()],
    ['set', utils.REDIS_KEY_2.decode(), utils.REDIS_VALUE_ALLOWED.decode()],
)
async def test_api_offers_status_with_multiple_hide_status(
        taxi_market_hide_offers_rt, teardown,
):
    await utils.prepare_abo_data(
        [
            utils.AboRule(utils.ID1, utils.YABS_ID1),
            utils.AboRule(utils.ID2, utils.YABS_ID2),
        ],
        taxi_market_hide_offers_rt,
    )

    request_info = utils.RequestInfo(utils.MOSCOW, [''])

    business_offer1 = utils.BusinessOffer(utils.ID1, utils.YABS_ID1, [''])
    service_offers1 = [
        utils.ServiceOffer(utils.ID1, [''], 'denied'),
        utils.ServiceOffer(utils.ID1, [''], 'denied'),
    ]

    business_offer2 = utils.BusinessOffer(utils.ID2, utils.YABS_ID2, [''])
    service_offers2 = [
        utils.ServiceOffer(utils.ID2, [''], 'denied'),
        utils.ServiceOffer(utils.ID2, [''], 'denied'),
    ]

    response = await taxi_market_hide_offers_rt.post(
        API,
        json=utils.prepare_request_data(
            [
                utils.Request(business_offer1, service_offers1, request_info),
                utils.Request(business_offer2, service_offers2, request_info),
            ],
        ),
    )

    assert response.status_code == 200
    assert response.json() == utils.prepare_response_data(
        [
            utils.Response(business_offer1, service_offers1),
            utils.Response(business_offer2, service_offers2),
        ],
    )


# Check api offers status for multiple offers expect 200
@pytest.mark.redis_store(
    ['set', utils.REDIS_KEY_1.decode(), utils.REDIS_VALUE_ALLOWED.decode()],
    ['set', utils.REDIS_KEY_2.decode(), utils.REDIS_VALUE_ALLOWED.decode()],
)
async def test_api_offers_status_with_multiple_status(
        taxi_market_hide_offers_rt, teardown,
):
    await utils.prepare_abo_data(
        [utils.AboRule(utils.ID1, utils.YABS_ID1)], taxi_market_hide_offers_rt,
    )

    request_info = utils.RequestInfo(utils.MOSCOW, [''])

    business_offer1 = utils.BusinessOffer(utils.ID1, utils.YABS_ID1, [''])
    service_offers1 = [
        utils.ServiceOffer(utils.ID1, [''], 'denied'),
        utils.ServiceOffer(utils.ID1, [''], 'denied'),
    ]

    business_offer2 = utils.BusinessOffer(utils.ID2, utils.YABS_ID2, [''])
    service_offers2 = [
        utils.ServiceOffer(utils.ID2, [''], 'allowed'),
        utils.ServiceOffer(utils.ID2, [''], 'allowed'),
    ]

    response = await taxi_market_hide_offers_rt.post(
        API,
        json=utils.prepare_request_data(
            [
                utils.Request(business_offer1, service_offers1, request_info),
                utils.Request(business_offer2, service_offers2, request_info),
            ],
        ),
    )

    assert response.status_code == 200
    assert response.json() == utils.prepare_response_data(
        [
            utils.Response(business_offer1, service_offers1),
            utils.Response(business_offer2, service_offers2),
        ],
    )

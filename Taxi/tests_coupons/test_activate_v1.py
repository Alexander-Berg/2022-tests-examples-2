import json

import pytest

from tests_coupons import util

YANDEX_UID = '4001'


@pytest.mark.config(COUPONS_SERVICE_ENABLED=False)
async def test_coupons_disabled(taxi_coupons):
    response = await util.make_activate_request_v1(
        taxi_coupons,
        data=util.mock_request_v1(
            yandex_uids=[YANDEX_UID],
            yandex_uid=YANDEX_UID,
            coupon='coupon',
            payment_info={'type': 'cash'},
            phone_id='5bbb5faf15870bd76635d5e2',
        ),
        headers={'X-Eats-User': 'personal_phone_id=5bbb5faf15870bd76635d5e2'},
    )
    assert response.status_code == 429


async def test_4xx(taxi_coupons):
    response = await util.make_activate_request_v1(taxi_coupons, data=None)
    assert response.status_code == 400

    response = await util.make_activate_request_v1(taxi_coupons, data={})
    assert response.status_code == 400


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.config(
    UAFS_COUPONS_FETCH_GLUE=True, UAFS_COUPONS_USE_GLUE_IN_TAXI_STATS=True,
)
async def test_simple_200(load_json, taxi_coupons, local_services, mockserver):
    @mockserver.json_handler('/user-statistics/v1/orders')
    def _mock_user_statistics(request):
        assert request.json == load_json(
            'simple_200_expected_statistics_request.json',
        )
        assert 'X-Ya-Service-Ticket' in request.headers
        return load_json('simple_200_statistics_response.json')

    @mockserver.handler('/uantifraud/v1/glue')
    def _mock_uafs(request):
        assert request.json == {
            'sources': ['taxi', 'eats'],
            'passport_uid': '4001',
        }
        return mockserver.make_response(
            json.dumps(
                {
                    'sources': {
                        'taxi': {'passport_uids': ['puid1', 'puid2', 'puid3']},
                        'eats': {'passport_uids': ['eats_uid1', 'eats_uid2']},
                    },
                },
            ),
            200,
        )

    local_services.add_card()
    expected = load_json('expected_activate_responses.json')
    response = await util.make_activate_request_v1(
        taxi_coupons,
        data=util.mock_request_v1(
            yandex_uids=[YANDEX_UID],
            yandex_uid=YANDEX_UID,
            coupon='MYYACODE',
            payment_info={'type': 'cash'},
            phone_id='5bbb5faf15870bd76635d5e2',
        ),
        headers={'X-Eats-User': 'personal_phone_id=5bbb5faf15870bd76635d5e2'},
    )
    assert response.status_code == 200
    assert expected['invalid'] == response.json()

    response = await util.make_activate_request_v1(
        taxi_coupons,
        data=util.mock_request_v1(
            yandex_uids=[YANDEX_UID],
            yandex_uid=YANDEX_UID,
            coupon='firstpromocode',
            payment_info={'type': 'cash'},
            phone_id='5bbb5faf15870bd76635d5e2',
        ),
        headers={'X-Eats-User': 'personal_phone_id=5bbb5faf15870bd76635d5e2'},
    )
    assert response.status_code == 200
    assert expected['valid'] == response.json()


@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_percent_100(load_json, taxi_coupons, local_services):
    local_services.add_card()
    expected = load_json('expected_activate_responses.json')
    response = await util.make_activate_request_v1(
        taxi_coupons,
        data=util.mock_request_v1(
            yandex_uids=[YANDEX_UID],
            yandex_uid=YANDEX_UID,
            coupon='promocode100',
            payment_info={'type': 'cash'},
            phone_id='5bbb5faf15870bd76635d5e2',
        ),
        headers={'X-Eats-User': 'personal_phone_id=5bbb5faf15870bd76635d5e2'},
    )
    assert response.status_code == 200
    assert expected['valid100'] == response.json()


@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_external_eda(taxi_coupons, local_services):
    local_services.add_card()
    response = await util.make_activate_request_v1(
        taxi_coupons,
        data=util.mock_request_v1(
            yandex_uids=[YANDEX_UID],
            yandex_uid=YANDEX_UID,
            coupon='promocodenonexisted',
            payment_info={'type': 'cash'},
            phone_id='5bbb5faf15870bd76635d5e2',
        ),
        headers={'X-Eats-User': 'personal_phone_id=5bbb5faf15870bd76635d5e2'},
    )
    assert response.status_code == 200
    assert response.json()['coupon']['status'] == 'invalid'

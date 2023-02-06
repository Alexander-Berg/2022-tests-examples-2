import pytest

from tests_coupons import util
from tests_coupons.referral import util as referral_util

HEADERS = {'X-Yandex-Uid': '75170007'}


@pytest.mark.parametrize(
    'headers', [None, HEADERS],  # headers are optional for now
)
@pytest.mark.parametrize(
    'params,expected_indexes',
    [
        pytest.param({}, [0, 1, 2, 3, 4, 5, 6], id='all campaigns'),
        pytest.param(
            {'brand_name': 'yataxi'}, [0, 1, 5], id='yataxi campaigns',
        ),
    ],
)
@pytest.mark.pgsql(
    referral_util.REFERRALS_DB_NAME, files=referral_util.PGSQL_REFERRAL,
)
@pytest.mark.now('2016-12-01T12:00:00.0')
async def test_campaigns_list(
        taxi_coupons, params, headers, expected_indexes, load_json,
):
    docs = load_json('campaigns_list.json')

    response = await taxi_coupons.get(
        '/admin/referral/campaigns/list/', params=params, headers=headers,
    )
    assert response.status_code == 200

    expected_json = {'items': [docs[i] for i in expected_indexes]}
    assert response.json() == expected_json


@pytest.mark.config(
    COUPONS_REFFERAL_SUPPORTED_SERVICES=['service_1', 'service_2'],
)
async def test_campaigns_options_list(taxi_coupons):
    response = await taxi_coupons.get(
        '/admin/referral/campaigns/options/list/',
    )

    response_json = util.sort_json(response.json(), 'supported_services')
    assert response.status_code == 200
    assert response_json == {
        'extra_checks': ['business_account'],
        'series_templates': ['brand', 'custom'],
        'supported_services': ['service_1', 'service_2'],
    }

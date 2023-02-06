import pytest

from tests_coupons.referral import util


HEADERS = {'X-Yandex-Uid': '75170007'}


@pytest.mark.parametrize(
    'headers', [None, HEADERS],  # headers are optional for now
)
@pytest.mark.parametrize(
    'params,expected_index',
    [
        pytest.param(
            {'campaign_name': 'common_taxi'}, 0, id='common_taxi campaign',
        ),
        pytest.param(
            {'campaign_name': 'not_existing_campaign'},
            -1,
            id='not existing campaign',
        ),
        pytest.param(
            {'campaign_name': 'grocery_referral'}, 6, id='grocery campaign',
        ),
    ],
)
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
@pytest.mark.now('2016-12-01T12:00:00.0')
async def test_campaigns_get(
        taxi_coupons, params, headers, expected_index, load_json,
):
    docs = load_json('campaigns_list.json')

    response = await taxi_coupons.get(
        '/admin/referral/campaigns/get/', params=params, headers=headers,
    )

    if expected_index < 0:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        expected_json = docs[expected_index]
        assert response.json() == expected_json

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
            {'campaign_name': 'common_taxi', 'id': 1},
            0,
            id='common_taxi cfgs',
        ),
        pytest.param(
            {'campaign_name': 'common_taxi', 'id': 0},
            -1,
            id='not existing id',
        ),
    ],
)
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_creator_configs_get(
        taxi_coupons, params, headers, expected_index, load_json,
):
    docs = load_json('creator_configs_list.json')

    response = await taxi_coupons.get(
        '/admin/referral/creator_configs/get/', params=params, headers=headers,
    )

    if expected_index < 0:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        expected_json = docs[expected_index]
        assert response.json() == expected_json, response.json()

import pytest

from tests_coupons.referral import util


HEADERS = {'X-Yandex-Uid': '75170007'}


@pytest.mark.parametrize(
    'headers', [None, HEADERS],  # headers are optional for now
)
@pytest.mark.parametrize(
    'params,expected_indexes',
    [
        pytest.param(
            {'campaign_name': 'common_taxi'},
            [0, 1, 2, 3],
            id='common_taxi cfgs',
        ),
        pytest.param(
            {'campaign_name': 'common_taxi', 'zone': 'moscow'},
            [0, 1],
            id='msk common_taxi cfgs',
        ),
        pytest.param(
            {'campaign_name': 'common_taxi', 'is_active': True},
            [0, 2, 3],
            id='active common_taxi cfgs',
        ),
        pytest.param(
            {'campaign_name': 'common_taxi', 'country': 'blr'},
            [],
            id='blr common_taxi cfgs',
        ),
        pytest.param(
            {'campaign_name': 'light_business'},
            [],
            id='no light_business cfgs',
        ),
    ],
)
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_consumer_configs_list(
        taxi_coupons, params, headers, expected_indexes, load_json,
):
    docs = load_json('consumer_configs_list.json')

    response = await taxi_coupons.get(
        '/admin/referral/consumer_configs/list/',
        params=params,
        headers=headers,
    )
    assert response.status_code == 200

    expected_json = {'items': [docs[i] for i in expected_indexes]}
    assert response.json() == expected_json, response.json()

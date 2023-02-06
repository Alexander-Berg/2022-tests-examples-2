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
            [0, 1, 2, 3, 4, 5, 6],
            id='common_taxi cfgs',
        ),
        pytest.param(
            {'campaign_name': 'common_taxi', 'is_active_for_new': True},
            [0, 1, 2, 3, 4, 5],
            id='active new common_taxi cfgs',
        ),
        pytest.param(
            {'campaign_name': 'common_taxi', 'is_active_for_new': False},
            [6],
            id='not new active common_taxi cfgs',
        ),
        pytest.param(
            {'campaign_name': 'common_taxi', 'country': 'usa'},
            [5, 6],
            id='usa common_taxi cfgs',
        ),
        pytest.param(
            {'campaign_name': 'common_taxi', 'zone': 'moscow'},
            [0],
            id='msk common_taxi cfgs',
        ),
    ],
)
@pytest.mark.pgsql(util.REFERRALS_DB_NAME, files=util.PGSQL_REFERRAL)
async def test_creator_configs_list(
        taxi_coupons, params, headers, expected_indexes, load_json,
):
    docs = load_json('creator_configs_list.json')

    response = await taxi_coupons.get(
        '/admin/referral/creator_configs/list/',
        params=params,
        headers=headers,
    )
    assert response.status_code == 200

    expected_json = {'items': [docs[i] for i in expected_indexes]}
    assert response.json() == expected_json, response.json()

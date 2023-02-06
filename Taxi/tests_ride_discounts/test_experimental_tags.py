import datetime

import pytest

from tests_ride_discounts import common


@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.parametrize(
    'personal_phone_id, has_match_discounts',
    (
        pytest.param('test_personal_phone_id', True),
        pytest.param('other_personal_phone_id', False),
    ),
)
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.config(
    RIDE_DISCOUNTS_FETCHING_DATA_SETTINGS={'experiments3': {'enabled': True}},
)
async def test_experimental_tags(
        client,
        load_json,
        mocked_time,
        personal_phone_id: str,
        has_match_discounts: bool,
):
    response = await client.post(
        'v1/admin/match-discounts/add-rules',
        headers=common.get_draft_headers(),
        json=load_json('add_rules_data.json'),
    )
    assert response.status == 200, response.json()

    mocked_time.set(
        datetime.datetime.fromisoformat('2019-01-04T18:00:00+00:00'),
    )
    await client.invalidate_caches()

    request_match_discounts = load_json('request_match_discounts.json')
    request_match_discounts['common_conditions']['user_info'][
        'personal_phone_id'
    ] = personal_phone_id
    response = await client.post(
        'v3/match-discounts/',
        headers=common.get_headers(),
        json=request_match_discounts,
    )
    assert response.status == 200
    assert has_match_discounts == bool(response.json()['discounts'])

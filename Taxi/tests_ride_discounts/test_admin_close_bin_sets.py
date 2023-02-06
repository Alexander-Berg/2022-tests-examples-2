import datetime
from typing import Dict
from typing import List
from typing import Optional

import pytest

from tests_ride_discounts import common

CLOSE_BIN_SETS_CHECK = '/v1/admin/close-bin-sets/check'
CLOSE_BIN_SETS = '/v1/admin/close-bin-sets/'


async def _add_discounts(add_rules, discounts_rules):
    for discount_rules in discounts_rules:
        add_rules_data = common.get_add_rules_data(
            {'payment_method_money_discounts'},
        )
        for discount_rule in discount_rules:
            for rule in add_rules_data['payment_method_money_discounts'][0][
                    'rules'
            ]:
                if rule['condition_name'] == discount_rule['condition_name']:
                    rule['values'] = discount_rule['values']
        await add_rules(add_rules_data)


@pytest.mark.parametrize(
    'bin_names, discounts_rules, close_bin_sets_time,'
    'expected_status_code, expected_response',
    (
        pytest.param(
            ['some_bins'],
            None,
            datetime.datetime(2019, 1, 1, 0, 0, 0),
            200,
            {
                'data': {'names': ['some_bins']},
                'lock_ids': [{'custom': False, 'id': 'some_bins'}],
            },
            id='no_active_discounts',
        ),
        pytest.param(
            ['invalid_bins'],
            None,
            datetime.datetime(2019, 1, 1, 0, 0, 0),
            400,
            'Operation is not possible. Some bin set not found',
            id='invalid_bin_name',
        ),
        pytest.param(
            ['some_bins'],
            [[{'condition_name': 'bins', 'values': ['some_bins']}]],
            datetime.datetime(2019, 9, 1, 0, 0, 0),
            400,
            'Operation is not possible. Bin used.',
            id='active_discounts_in_the_future',
        ),
        pytest.param(
            ['some_bins'],
            [[{'condition_name': 'bins', 'values': ['some_bins']}]],
            datetime.datetime(2020, 6, 1, 0, 0, 0),
            400,
            'Operation is not possible. Bin used.',
            id='active_discounts_now',
        ),
        pytest.param(
            ['some_bins'],
            [[{'condition_name': 'bins', 'values': ['some_bins']}]],
            datetime.datetime(2021, 6, 1, 0, 0, 0),
            200,
            {
                'data': {'names': ['some_bins']},
                'lock_ids': [{'custom': False, 'id': 'some_bins'}],
            },
            id='discounts_in_the_past',
        ),
    ),
)
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
@pytest.mark.now('2019-01-01T00:00:00+00:00')
async def test_close_bin_sets(
        client,
        add_rules,
        mocked_time,
        bin_names: List[str],
        discounts_rules: Optional[List[List[Dict]]],
        close_bin_sets_time: datetime.datetime,
        expected_status_code: int,
        expected_response: Optional[dict],
):
    await common.init_bin_sets(client)

    if discounts_rules:
        await _add_discounts(add_rules, discounts_rules)

    mocked_time.set(close_bin_sets_time)

    request: dict = {'names': bin_names}
    response = await client.post(
        CLOSE_BIN_SETS_CHECK, request, headers=common.get_headers(),
    )
    response_json = response.json()
    assert response.status_code == expected_status_code, response_json
    if expected_status_code != 200:
        if expected_response is not None:
            assert response_json.get('message') == expected_response
    else:
        assert response_json == expected_response

    headers = common.get_draft_headers('draft_id_close_bin_sets')
    response = await client.post(CLOSE_BIN_SETS, request, headers=headers)
    assert response.status_code == expected_status_code
    if expected_status_code == 200:
        mocked_time.set(close_bin_sets_time + datetime.timedelta(seconds=1))
        response = await client.get(
            common.PRIORITY_URL,
            params={'prioritized_entity_type': 'bin_set'},
            headers=common.get_headers(),
        )
        assert response.status_code == 200
        assert response.json()['priority_groups'][0]['entities_names'] == []

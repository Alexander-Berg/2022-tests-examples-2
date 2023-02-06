from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pytest

from tests_ride_discounts import common


PATH_ADD_RULES = '/v1/admin/match-discounts/add-rules'


def _get_add_rules_json(
        payment_method_values: Optional[Union[List[str], str]],
        payment_method_exclusions: Optional[List[str]],
) -> Dict[str, Any]:
    add_rules_json: Dict[str, Any] = {
        'series_id': '78563307-7501-42c2-9468-e63f727ddaa4',
        'affected_discount_ids': [],
        'data': {
            'discount': common.make_discount(
                hierarchy_name='experimental_money_discounts',
            ),
            'hierarchy_name': 'experimental_money_discounts',
        },
        'rules': [
            {
                'condition_name': 'active_period',
                'values': [
                    {
                        'end': '2021-07-08T15:00:00+00:00',
                        'is_end_utc': True,
                        'is_start_utc': True,
                        'start': '2021-06-25T18:00:00+00:00',
                    },
                ],
            },
            {
                'condition_name': 'zone',
                'values': [
                    {
                        'is_prioritized': False,
                        'name': 'moscow',
                        'type': 'tariff_zone',
                    },
                ],
            },
        ],
    }
    if payment_method_values is not None:
        condition_payment_method = {
            'condition_name': 'payment_method',
            'values': payment_method_values,
        }
        if payment_method_exclusions is not None:
            condition_payment_method['exclusions'] = payment_method_exclusions
        add_rules_json['rules'].append(condition_payment_method)
    return add_rules_json


async def _add_rules_request(client, add_rules_json: Dict[str, Any]):
    response = await client.post(
        PATH_ADD_RULES,
        headers=common.get_draft_headers(),
        json=add_rules_json,
    )
    return response


@pytest.mark.parametrize(
    'payment_method_values, payment_method_exclusions,'
    'config_value, excepted_status',
    (
        pytest.param(
            None, None, [], 200, id='without_payment_method_and_config',
        ),
        pytest.param(
            None,
            None,
            ['corp', 'not_support'],
            400,
            id='without_payment_method',
        ),
        pytest.param(
            ['money', 'cart'],
            None,
            ['corp', 'not_support'],
            200,
            id='good_request',
        ),
        pytest.param(
            ['not_support', 'corp'],
            None,
            ['corp', 'not_support'],
            400,
            id='2_not_suppotred_methods',
        ),
        pytest.param(
            ['corp'],
            None,
            ['corp', 'not_support'],
            400,
            id='1_not_suppotred_methods',
        ),
        pytest.param(
            'Other',
            None,
            ['corp', 'not_support'],
            400,
            id='all_without_exclusions',
        ),
        pytest.param(
            'Other',
            [],
            ['corp', 'not_support'],
            400,
            id='all_empty_exclusions',
        ),
        pytest.param(
            'Other',
            ['corp', 'not_support'],
            ['corp', 'not_support'],
            200,
            id='good_request_all',
        ),
        pytest.param(
            'Other',
            ['money', 'corp'],
            ['corp', 'not_support'],
            400,
            id='all_without_1_method',
        ),
    ),
)
@pytest.mark.now('2019-01-01T00:00:00+00:00')
@pytest.mark.pgsql('ride_discounts', files=['init.sql'])
async def test_add_rules_payment_method(
        client,
        taxi_config,
        payment_method_values: Optional[Union[List[str], str]],
        payment_method_exclusions: Optional[List[str]],
        config_value: List[str],
        excepted_status: int,
):
    """
    Checking whether it is possible to create a discount
    with different sets of unsupported methods
    """
    taxi_config.set(
        RIDE_DISCOUNTS_NOT_SUPPORTED_PAYMENT_METHODS={
            'payment_methods': config_value,
        },
    )
    json_add_rules: Dict[str, Any] = _get_add_rules_json(
        payment_method_values, payment_method_exclusions,
    )
    response = await _add_rules_request(client, json_add_rules)
    assert response.status_code == excepted_status
    if response.status_code == 400:
        assert response.json() == {
            'code': 'Validation error',
            'message': common.StartsWith('Payment methods \''),
        }

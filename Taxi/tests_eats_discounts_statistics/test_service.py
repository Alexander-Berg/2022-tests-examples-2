import uuid
from typing import List

import pytest

# flake8: noqa
# pylint: disable=import-error,wildcard-import
from eats_discounts_statistics_plugins.generated_tests import *

ORDER_ID = '123'
DISCOUNTS = [
    {'discount_id': 1, 'discount_value': 10},
    {'discount_id': 2, 'discount_value': 20},
]
PERSONAL_PHONE_ID = 'test_personal_phone_id'
EATER_ID = 'test_eater_id'
YANDEX_UID = 'test_yandex_uid'

DISCOUNT_USAGES = [
    {
        'order_id': ORDER_ID,
        'discounts': DISCOUNTS,
        'time': '2022-03-10T10:42:02+00:00',
        'eater_id': EATER_ID,
        'yandex_uid': YANDEX_UID,
        'personal_phone_id': PERSONAL_PHONE_ID,
    },
]

DISCOUNT_USAGES_WITH_OPTIONAL = [
    {
        'order_id': ORDER_ID,
        'discounts': DISCOUNTS,
        'time': '2022-03-10T10:42:02+00:00',
        'yandex_uid': YANDEX_UID,
    },
]


async def _create_discount_usages(stq_runner, discount_usages: List[dict]):
    for kwargs in discount_usages:
        await stq_runner.eats_discounts_statistics_add.call(
            task_id=str(uuid.uuid4()), kwargs=kwargs,
        )


@pytest.mark.parametrize(
    'request_data, cancel_kwargs, expected_response, discount_usages',
    (
        pytest.param(
            {
                'eater_id': EATER_ID,
                'yandex_uid': YANDEX_UID,
                'personal_phone_id': PERSONAL_PHONE_ID,
            },
            None,
            {
                'items': [
                    {
                        'count_usages': 1,
                        'discount_id': 1,
                        'spent_budget': 10.0,
                    },
                    {
                        'count_usages': 1,
                        'discount_id': 2,
                        'spent_budget': 20.0,
                    },
                ],
            },
            DISCOUNT_USAGES,
            id='by_all_identifiers',
        ),
        pytest.param(
            {'eater_id': 'invalid'},
            None,
            {'items': []},
            DISCOUNT_USAGES,
            id='by_invalid_identifier',
        ),
        pytest.param(
            {
                'eater_id': 'invalid',
                'yandex_uid': YANDEX_UID,
                'personal_phone_id': PERSONAL_PHONE_ID,
            },
            None,
            {
                'items': [
                    {
                        'count_usages': 1,
                        'discount_id': 1,
                        'spent_budget': 10.0,
                    },
                    {
                        'count_usages': 1,
                        'discount_id': 2,
                        'spent_budget': 20.0,
                    },
                ],
            },
            DISCOUNT_USAGES,
            id='with_invalid_identifiers',
        ),
        pytest.param(
            {'yandex_uid': YANDEX_UID},
            None,
            {
                'items': [
                    {
                        'count_usages': 1,
                        'discount_id': 1,
                        'spent_budget': 10.0,
                    },
                    {
                        'count_usages': 1,
                        'discount_id': 2,
                        'spent_budget': 20.0,
                    },
                ],
            },
            DISCOUNT_USAGES,
            id='by_yandex_uid',
        ),
        pytest.param(
            {'eater_id': EATER_ID},
            None,
            {
                'items': [
                    {
                        'count_usages': 1,
                        'discount_id': 1,
                        'spent_budget': 10.0,
                    },
                    {
                        'count_usages': 1,
                        'discount_id': 2,
                        'spent_budget': 20.0,
                    },
                ],
            },
            DISCOUNT_USAGES,
            id='by_eater_id',
        ),
        pytest.param(
            {}, None, {'items': []}, DISCOUNT_USAGES, id='without_identifiers',
        ),
        pytest.param(
            {'personal_phone_id': PERSONAL_PHONE_ID},
            None,
            {
                'items': [
                    {
                        'count_usages': 1,
                        'discount_id': 1,
                        'spent_budget': 10.0,
                    },
                    {
                        'count_usages': 1,
                        'discount_id': 2,
                        'spent_budget': 20.0,
                    },
                ],
            },
            DISCOUNT_USAGES,
            id='by_personal_phone_id',
        ),
        pytest.param(
            {'personal_phone_id': PERSONAL_PHONE_ID},
            {'order_id': ORDER_ID, 'discounts': DISCOUNTS},
            {'items': []},
            DISCOUNT_USAGES,
            id='both_cancelled',
        ),
        pytest.param(
            {'personal_phone_id': PERSONAL_PHONE_ID},
            {
                'order_id': ORDER_ID,
                'discounts': [
                    {'discount_id': 1, 'discount_value': 9.50},
                    {'discount_id': 2, 'discount_value': 11.5},
                ],
            },
            {
                'items': [
                    {'count_usages': 1, 'discount_id': 1, 'spent_budget': 0.5},
                    {'count_usages': 1, 'discount_id': 2, 'spent_budget': 8.5},
                ],
            },
            DISCOUNT_USAGES,
            id='partial_cancelled',
        ),
        pytest.param(
            {'personal_phone_id': PERSONAL_PHONE_ID},
            {'order_id': ORDER_ID, 'discounts': DISCOUNTS[:1]},
            {
                'items': [
                    {
                        'count_usages': 1,
                        'discount_id': 2,
                        'spent_budget': 20.0,
                    },
                ],
            },
            DISCOUNT_USAGES,
            id='one_cancelled',
        ),
        pytest.param(
            {'personal_phone_id': PERSONAL_PHONE_ID},
            None,
            {'items': []},
            DISCOUNT_USAGES_WITH_OPTIONAL,
            id='no_match_due_to_optionality',
        ),
        pytest.param(
            {'yandex_uid': YANDEX_UID},
            None,
            {
                'items': [
                    {
                        'count_usages': 1,
                        'discount_id': 1,
                        'spent_budget': 10.0,
                    },
                    {
                        'count_usages': 1,
                        'discount_id': 2,
                        'spent_budget': 20.0,
                    },
                ],
            },
            DISCOUNT_USAGES_WITH_OPTIONAL,
            id='matching_the_search_with_optional_fields',
        ),
    ),
)
async def test_statistics(
        client,
        stq_runner,
        request_data: dict,
        cancel_kwargs,
        expected_response,
        discount_usages: List[dict],
):
    await _create_discount_usages(stq_runner, discount_usages)

    if cancel_kwargs is not None:
        await stq_runner.eats_discounts_statistics_cancel.call(
            task_id=str(uuid.uuid4()), kwargs=cancel_kwargs,
        )
    response = await client.post('v1/get', json=request_data)
    assert response.json() == expected_response

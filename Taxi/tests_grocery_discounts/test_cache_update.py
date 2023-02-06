import datetime
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple

import pytest

from tests_grocery_discounts import common

DISTANT_PAST = ('2000-01-01T09:00:01+00:00', '2001-01-01T00:00:00+00:00')
PAST = ('2019-01-01T09:00:01+00:00', '2020-01-01T00:00:00+00:00')
FUTURE = ('2021-01-01T09:00:01+00:00', '2022-01-01T00:00:00+00:00')
DISTANT_FUTURE = ('2049-01-01T09:00:01+00:00', '2050-01-01T00:00:00+00:00')

YEAR_SEC = datetime.timedelta(days=365).total_seconds()

ALL_TIME_RANGES = (DISTANT_PAST, PAST, FUTURE, DISTANT_FUTURE)

COMMON_CONDITIONS = {
    'cities': ['213'],
    'countries': ['some_country'],
    'depots': ['some_depot'],
}


def _get_rules(time_range: Tuple[str, str]) -> List[dict]:
    return [
        {
            'condition_name': 'active_period',
            'values': [
                {
                    'start': time_range[0],
                    'is_start_utc': False,
                    'is_end_utc': False,
                    'end': time_range[1],
                },
            ],
        },
        {'condition_name': 'city', 'values': ['213']},
        {'condition_name': 'country', 'values': ['some_country']},
        {'condition_name': 'depot', 'values': ['some_depot']},
    ]


def _get_add_rules_data() -> dict:
    result: dict = {'menu_discounts': []}
    discounts = result['menu_discounts']
    for idx, time_range in enumerate(ALL_TIME_RANGES):
        discounts.append(
            {
                'rules': _get_rules(time_range),
                'discount': common.small_menu_discount(str(idx)),
            },
        )
    return result


def _get_discount_results(
        add_rules_data: dict, idx: int, discount_expected: bool,
) -> List[dict]:
    discounts = []
    if discount_expected:
        discounts.append(
            {
                'discount': common.get_matched_discount(
                    add_rules_data, 'menu_discounts', 0, idx,
                ),
                'match_path': [],
                'create_draft_id': 'draft_id_check_add_rules_validation',
            },
        )
    return [
        {
            'discounts': discounts,
            'status': 'ok',
            'hierarchy_name': 'menu_discounts',
        },
    ]


CACHE_UPDATE_TEST_PARAMS = pytest.mark.parametrize(
    'cache_settings, expected_times',
    (
        pytest.param(
            {'__default__': {'hierarchies_settings': {'__default__': {}}}},
            set(ALL_TIME_RANGES),
            id='default',
        ),
        pytest.param(
            {
                '__default__': {
                    'hierarchies_settings': {
                        '__default__': {
                            'load_time_range_settings': {
                                'condition_name': 'active_period',
                            },
                        },
                    },
                },
            },
            set(ALL_TIME_RANGES),
            id='only_condition_name',
        ),
        pytest.param(
            {
                '__default__': {
                    'hierarchies_settings': {
                        '__default__': {
                            'load_time_range_settings': {
                                'condition_name': 'active_period',
                                'past_delta_sec': 2 * YEAR_SEC,
                            },
                        },
                    },
                },
            },
            {PAST, FUTURE, DISTANT_FUTURE},
            id='only_past_delta',
        ),
        pytest.param(
            {
                '__default__': {
                    'hierarchies_settings': {
                        '__default__': {
                            'load_time_range_settings': {
                                'condition_name': 'active_period',
                                'future_delta_sec': 2 * YEAR_SEC,
                            },
                        },
                    },
                },
            },
            {DISTANT_PAST, PAST, FUTURE},
            id='only_future_delta',
        ),
        pytest.param(
            {
                '__default__': {
                    'hierarchies_settings': {
                        '__default__': {
                            'load_time_range_settings': {
                                'condition_name': 'active_period',
                                'past_delta_sec': 2 * YEAR_SEC,
                                'future_delta_sec': 2 * YEAR_SEC,
                            },
                        },
                    },
                },
            },
            {PAST, FUTURE},
            id='past_and_future_delta',
        ),
        pytest.param(
            {
                '__default__': {'hierarchies_settings': {'__default__': {}}},
                'grocery_discounts': {
                    'hierarchies_settings': {
                        '__default__': {
                            'load_time_range_settings': {
                                'condition_name': 'active_period',
                                'past_delta_sec': 2 * YEAR_SEC,
                                'future_delta_sec': 2 * YEAR_SEC,
                            },
                        },
                    },
                },
            },
            {PAST, FUTURE},
            id='schema_specified',
        ),
        pytest.param(
            {
                '__default__': {'hierarchies_settings': {'__default__': {}}},
                'grocery_discounts': {
                    'hierarchies_settings': {
                        '__default__': {},
                        'menu_discounts': {
                            'load_time_range_settings': {
                                'condition_name': 'active_period',
                                'past_delta_sec': 2 * YEAR_SEC,
                                'future_delta_sec': 2 * YEAR_SEC,
                            },
                        },
                    },
                },
            },
            {PAST, FUTURE},
            id='hierarchy_specified',
        ),
        pytest.param(
            {
                '__default__': {'hierarchies_settings': {'__default__': {}}},
                'another_schema': {
                    'hierarchies_settings': {
                        '__default__': {
                            'load_time_range_settings': {
                                'condition_name': 'active_period',
                                'past_delta_sec': 2 * YEAR_SEC,
                                'future_delta_sec': 2 * YEAR_SEC,
                            },
                        },
                    },
                },
            },
            set(ALL_TIME_RANGES),
            id='another_schema',
        ),
        pytest.param(
            {
                '__default__': {'hierarchies_settings': {'__default__': {}}},
                'grocery_discounts': {
                    'hierarchies_settings': {
                        '__default__': {},
                        'another_hierarchy': {
                            'load_time_range_settings': {
                                'condition_name': 'active_period',
                                'past_delta_sec': 2 * YEAR_SEC,
                                'future_delta_sec': 2 * YEAR_SEC,
                            },
                        },
                    },
                },
            },
            set(ALL_TIME_RANGES),
            id='another_hierarchy',
        ),
        pytest.param(
            {
                '__default__': {
                    'hierarchies_settings': {
                        '__default__': {
                            'load_time_range_settings': {
                                'condition_name': 'missing_condition',
                            },
                        },
                    },
                },
            },
            set(ALL_TIME_RANGES),
            id='only_missing_condition_name',
        ),
        pytest.param(
            {
                '__default__': {
                    'hierarchies_settings': {
                        '__default__': {
                            'load_time_range_settings': {
                                'condition_name': 'missing_condition',
                                'past_delta_sec': 2 * YEAR_SEC,
                                'future_delta_sec': 2 * YEAR_SEC,
                            },
                        },
                    },
                },
            },
            set(ALL_TIME_RANGES),
            id='missing_condition_name',
        ),
        pytest.param(
            {
                '__default__': {
                    'hierarchies_settings': {
                        '__default__': {
                            'load_time_range_settings': {
                                'condition_name': 'experiment',
                                'past_delta_sec': 2 * YEAR_SEC,
                                'future_delta_sec': 2 * YEAR_SEC,
                            },
                        },
                    },
                },
            },
            set(ALL_TIME_RANGES),
            id='wrong_any_other_condition',
        ),
        pytest.param(
            {
                '__default__': {
                    'hierarchies_settings': {
                        '__default__': {
                            'load_time_range_settings': {
                                'condition_name': 'class',
                                'past_delta_sec': 2 * YEAR_SEC,
                                'future_delta_sec': 2 * YEAR_SEC,
                            },
                        },
                    },
                },
            },
            set(ALL_TIME_RANGES),
            id='wrong_type_condition',
        ),
    ),
)


@CACHE_UPDATE_TEST_PARAMS
@pytest.mark.pgsql('grocery_discounts', files=['init.sql'])
@pytest.mark.now('2020-01-01T00:00:00+00:00')
async def test_update_cache(
        client,
        taxi_config,
        mocked_time,
        add_rules,
        cache_settings: Optional[dict],
        expected_times: Set[Tuple[str, str]],
) -> None:
    now = mocked_time.now()
    mocked_time.set(datetime.datetime(1970, 1, 1))
    add_rules_data = _get_add_rules_data()
    await add_rules(add_rules_data)
    mocked_time.set(now)
    taxi_config.set(DISCOUNTS_MATCH_CACHE_SETTINGS=cache_settings)
    await client.invalidate_caches()

    for idx, time_range in enumerate(ALL_TIME_RANGES):
        results = _get_discount_results(
            add_rules_data, idx, time_range in expected_times,
        )
        await common.check_match_discounts(
            client,
            ['menu_discounts'],
            [],
            COMMON_CONDITIONS,
            time_range[0],
            'UTC',
            False,
            {
                'match_results': [
                    {'subquery_id': 'no_subquery_id', 'results': results},
                ],
            },
            200,
        )

import datetime

import pytest

from chatterbox.crontasks import calculate_stat
from chatterbox.internal import stat


NOW = datetime.datetime(2018, 10, 26, 23, 27, 1)  # 27-е число по Москве
ONLY_ACTIONS_NOW = datetime.datetime(2019, 10, 23, 23, 27, 1)


async def test_moscow_time():
    # 2018-12-10 00:00 по Москве
    moscow_midnight = datetime.datetime(2018, 12, 9, 21, 0)
    for i in range(24):
        assert (
            calculate_stat.utc_datetime_to_moscow_day(
                moscow_midnight + datetime.timedelta(hours=i),
            )
            == '2018-12-10'
        )

    assert (
        calculate_stat.moscow_day_to_utc_datetime('2018-12-10')
        == moscow_midnight
    )


async def get_test_stat(context, day, in_addition=None):
    result = await context.data.db.support_chatterbox_stat.find_one(
        {'day': day, 'in_addition': stat.get_in_addition_query(in_addition)},
        {'_id': False},
    )
    result['lines_statistics'].sort(key=lambda stat: stat['line'])
    return result


@pytest.mark.now(NOW.isoformat())
async def test_calculate_stat(cbox_context, loop):
    await calculate_stat.do_stuff(cbox_context, loop)

    statistics = await get_test_stat(cbox_context, '2018-10-27')
    assert statistics == {
        'completed': False,
        'day': '2018-10-27',
        'lines_statistics': [
            {
                'line': 'first',
                'count': 3,
                'first_answer_median': 1000,
                'full_resolve_median': 2000,
                'actions': [
                    {
                        'action_id': 'close',
                        'average_latency': 60.0,
                        'count': 1,
                        'max_latency': 60,
                        'min_latency': 60,
                    },
                ],
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'close',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'somebody',
                    },
                ],
            },
            {
                'line': 'urgent',
                'count': 2,
                'first_answer_median': 200,
                'full_resolve_median': 400,
                'actions': [],
                'actions_by_supporter': [],
            },
        ],
        'total_statistics': {
            'count': 5,
            'first_answer_median': 200,
            'full_resolve_median': 400,
            'actions': [
                {
                    'action_id': 'close',
                    'average_latency': 60.0,
                    'count': 1,
                    'max_latency': 60,
                    'min_latency': 60,
                },
            ],
            'actions_by_supporter': [
                {
                    'actions': [
                        {
                            'action_id': 'close',
                            'average_latency': 60.0,
                            'count': 1,
                            'max_latency': 60,
                            'min_latency': 60,
                        },
                    ],
                    'login': 'somebody',
                },
            ],
        },
    }

    statistics = await get_test_stat(cbox_context, '2018-10-27', False)
    assert statistics == {
        'completed': False,
        'day': '2018-10-27',
        'in_addition': False,
        'lines_statistics': [
            {
                'actions': [],
                'actions_by_supporter': [],
                'count': 2,
                'first_answer_median': 10000,
                'full_resolve_median': 20000,
                'line': 'first',
            },
            {
                'actions': [],
                'actions_by_supporter': [],
                'count': 2,
                'first_answer_median': 200,
                'full_resolve_median': 400,
                'line': 'urgent',
            },
        ],
        'total_statistics': {
            'actions': [],
            'actions_by_supporter': [],
            'count': 4,
            'first_answer_median': 1000,
            'full_resolve_median': 2000,
        },
    }

    statistics = await get_test_stat(cbox_context, '2018-10-27', True)
    assert statistics == {
        'completed': False,
        'day': '2018-10-27',
        'in_addition': True,
        'lines_statistics': [
            {
                'actions': [
                    {
                        'action_id': 'close',
                        'average_latency': 60.0,
                        'count': 1,
                        'max_latency': 60,
                        'min_latency': 60,
                    },
                ],
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'close',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'somebody',
                    },
                ],
                'count': 1,
                'first_answer_median': 100,
                'full_resolve_median': 200,
                'line': 'first',
            },
        ],
        'total_statistics': {
            'actions': [
                {
                    'action_id': 'close',
                    'average_latency': 60.0,
                    'count': 1,
                    'max_latency': 60,
                    'min_latency': 60,
                },
            ],
            'actions_by_supporter': [
                {
                    'actions': [
                        {
                            'action_id': 'close',
                            'average_latency': 60.0,
                            'count': 1,
                            'max_latency': 60,
                            'min_latency': 60,
                        },
                    ],
                    'login': 'somebody',
                },
            ],
            'count': 1,
            'first_answer_median': 100,
            'full_resolve_median': 200,
        },
    }

    statistics = await get_test_stat(cbox_context, '2018-10-26')
    assert statistics == {
        'completed': True,
        'day': '2018-10-26',
        'lines_statistics': [
            {
                'actions': [
                    {
                        'action_id': 'close',
                        'average_latency': 60.0,
                        'count': 1,
                        'max_latency': 60,
                        'min_latency': 60,
                    },
                ],
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'close',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'somebody',
                    },
                ],
                'count': 1,
                'first_answer_median': 100,
                'full_resolve_median': 200,
                'line': 'first',
            },
        ],
        'total_statistics': {
            'actions': [
                {
                    'action_id': 'close',
                    'average_latency': 60.0,
                    'count': 1,
                    'max_latency': 60,
                    'min_latency': 60,
                },
            ],
            'actions_by_supporter': [
                {
                    'actions': [
                        {
                            'action_id': 'close',
                            'average_latency': 60.0,
                            'count': 1,
                            'max_latency': 60,
                            'min_latency': 60,
                        },
                    ],
                    'login': 'somebody',
                },
            ],
            'count': 1,
            'first_answer_median': 100,
            'full_resolve_median': 200,
        },
    }

    statistics = await get_test_stat(cbox_context, '2018-10-26', False)
    assert statistics == {
        'completed': True,
        'day': '2018-10-26',
        'in_addition': False,
        'lines_statistics': [
            {
                'actions': [
                    {
                        'action_id': 'close',
                        'average_latency': 60.0,
                        'count': 1,
                        'max_latency': 60,
                        'min_latency': 60,
                    },
                ],
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'close',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'somebody',
                    },
                ],
                'count': 1,
                'first_answer_median': 100,
                'full_resolve_median': 200,
                'line': 'first',
            },
        ],
        'total_statistics': {
            'actions': [
                {
                    'action_id': 'close',
                    'average_latency': 60.0,
                    'count': 1,
                    'max_latency': 60,
                    'min_latency': 60,
                },
            ],
            'actions_by_supporter': [
                {
                    'actions': [
                        {
                            'action_id': 'close',
                            'average_latency': 60.0,
                            'count': 1,
                            'max_latency': 60,
                            'min_latency': 60,
                        },
                    ],
                    'login': 'somebody',
                },
            ],
            'count': 1,
            'first_answer_median': 100,
            'full_resolve_median': 200,
        },
    }

    statistics = await get_test_stat(cbox_context, '2018-10-26', True)
    assert statistics == {
        'completed': True,
        'day': '2018-10-26',
        'in_addition': True,
        'lines_statistics': [],
        'total_statistics': {
            'actions': [],
            'actions_by_supporter': [],
            'count': 0,
        },
    }


# test case: line had actions but without count,first_reply,full_resolve
@pytest.mark.now(ONLY_ACTIONS_NOW.isoformat())
async def test_only_actions_calculate_stat(cbox_context, loop):
    await calculate_stat.do_stuff(cbox_context, loop)

    statistics = await get_test_stat(cbox_context, '2019-10-24', True)
    assert statistics == {
        'completed': False,
        'day': '2019-10-24',
        'in_addition': True,
        'lines_statistics': [
            {
                'actions': [
                    {
                        'action_id': 'close',
                        'average_latency': 60.0,
                        'count': 1,
                        'max_latency': 60,
                        'min_latency': 60,
                    },
                ],
                'actions_by_supporter': [
                    {
                        'actions': [
                            {
                                'action_id': 'close',
                                'average_latency': 60.0,
                                'count': 1,
                                'max_latency': 60,
                                'min_latency': 60,
                            },
                        ],
                        'login': 'somebody',
                    },
                ],
                'count': 0,
                'line': 'first',
            },
        ],
        'total_statistics': {
            'actions': [
                {
                    'action_id': 'close',
                    'average_latency': 60.0,
                    'count': 1,
                    'max_latency': 60,
                    'min_latency': 60,
                },
            ],
            'actions_by_supporter': [
                {
                    'actions': [
                        {
                            'action_id': 'close',
                            'average_latency': 60.0,
                            'count': 1,
                            'max_latency': 60,
                            'min_latency': 60,
                        },
                    ],
                    'login': 'somebody',
                },
            ],
            'count': 0,
        },
    }

# pylint: disable=redefined-outer-name
import os

from aiohttp import web
import pandas as pd
import pytest

import discounts_operation_calculations.generated.service.pytest_init  # noqa: F401,E501 pylint: disable=C0301
from discounts_operation_calculations.generated.stq3.yt_wrapper import plugin
from discounts_operation_calculations.internals import helpers

pytest_plugins = [
    'discounts_operation_calculations.generated.service.pytest_plugins',
]


class SegmentStatsLoaderMock:
    def __init__(self, *args, **kwargs):
        pass

    async def load_from_yt_to_pg(self, *args, **kwargs):
        pass

    async def clear_prev_results(self, *args, **kwargs):
        pass


class MockAsyncYTClient(plugin.AsyncYTClient):
    async def exists(self, *args, **kwargs):
        return False


@pytest.fixture
def mock_yt_client(patch):
    @patch(
        'discounts_operation_calculations.generated.stq3.yt_wrapper.'
        'plugin.AsyncYTClient',
    )
    def _yt_client_mock(*args, **kwargs):
        return MockAsyncYTClient(*args, **kwargs)


@pytest.fixture
def load_dataframe_from_csv(request):
    def _load_dataframe(filename, *args, **kwargs):
        static_dir = os.path.join(
            os.path.dirname(request.node.fspath),
            'static',
            os.path.basename(request.node.fspath).replace('.py', ''),
        )
        return pd.read_csv(os.path.join(static_dir, filename), *args, **kwargs)

    return _load_dataframe


@pytest.fixture
def submission_id():
    return 'random_submission_id'


@pytest.fixture
def calc_segment_stats_mock(patch, submission_id):
    @patch('discounts_operation_calculations.utils.spark_submit._spark_submit')
    async def _spark_submit(*args, **kwargs):
        return submission_id

    @patch('discounts_operation_calculations.utils.spark_submit.poll')
    async def _poll(*args, **kwargs):
        return 'FINISHED'

    @patch(
        'discounts_operation_calculations.internals.segment_stats_loader_v2.'
        'SegmentStatsLoader',
    )
    def _mock_segment_stats_loader(*args, **kwargs):
        return SegmentStatsLoaderMock(*args, **kwargs)

    @patch(
        'discounts_operation_calculations.generated.stq3.yt_wrapper.'
        'plugin.AsyncYTClient',
    )
    def _yt_client_mock(*args, **kwargs):
        return MockAsyncYTClient(*args, **kwargs)


ELASTICITIES_DICT = {
    '__default__': {
        '__default__': {
            'default': {
                '0': {
                    'elasticity': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    'multiapp_coef': 1,
                    'price_bucket': [
                        50,
                        100,
                        150,
                        200,
                        250,
                        300,
                        350,
                        400,
                        450,
                        500,
                        550,
                        600,
                        650,
                    ],
                },
                '1': {
                    'elasticity': [
                        1.5,
                        1.5,
                        1.5,
                        1.5,
                        1.6,
                        1.6,
                        1.6,
                        1.6,
                        1.6,
                        1.6,
                        1.7,
                        1.7,
                        1.7,
                    ],
                    'multiapp_coef': 1,
                    'price_bucket': [
                        50,
                        100,
                        150,
                        200,
                        250,
                        300,
                        350,
                        400,
                        450,
                        500,
                        550,
                        600,
                        650,
                    ],
                },
                '2': {
                    'elasticity': [
                        1.7,
                        1.7,
                        1.7,
                        1.7,
                        1.9,
                        1.9,
                        1.9,
                        1.9,
                        1.9,
                        2.1,
                        2.1,
                        2.1,
                        2.1,
                    ],
                    'multiapp_coef': 1,
                    'price_bucket': [
                        50,
                        100,
                        150,
                        200,
                        250,
                        300,
                        350,
                        400,
                        450,
                        500,
                        550,
                        600,
                        650,
                    ],
                },
                '3': {
                    'elasticity': [
                        1.9,
                        1.9,
                        1.9,
                        1.9,
                        2.1,
                        2.1,
                        2.1,
                        2.1,
                        2.3,
                        2.3,
                        2.3,
                        2.3,
                        2.3,
                    ],
                    'multiapp_coef': 1,
                    'price_bucket': [
                        50,
                        100,
                        150,
                        200,
                        250,
                        300,
                        350,
                        400,
                        450,
                        500,
                        550,
                        600,
                        650,
                    ],
                },
                'random': {
                    'elasticity': [
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                    ],
                    'multiapp_coef': 1,
                    'price_bucket': [
                        50,
                        100,
                        150,
                        200,
                        250,
                        300,
                        350,
                        400,
                        450,
                        500,
                        550,
                        600,
                        650,
                    ],
                },
            },
            'push': {
                '0': {
                    'elasticity': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    'multiapp_coef': 1,
                    'price_bucket': [
                        50,
                        100,
                        150,
                        200,
                        250,
                        300,
                        350,
                        400,
                        450,
                        500,
                        550,
                        600,
                        650,
                    ],
                },
                '1': {
                    'elasticity': [
                        0.6,
                        0.6,
                        0.7,
                        0.9,
                        0.9,
                        1,
                        1,
                        1.1,
                        1.1,
                        1.1,
                        1.2,
                        1.2,
                        1.2,
                    ],
                    'multiapp_coef': 1,
                    'price_bucket': [
                        50,
                        100,
                        150,
                        200,
                        250,
                        300,
                        350,
                        400,
                        450,
                        500,
                        550,
                        600,
                        650,
                    ],
                },
                '2': {
                    'elasticity': [
                        1.3,
                        1.3,
                        1.3,
                        1.5,
                        1.5,
                        2.2,
                        2.2,
                        2.2,
                        2.3,
                        2.4,
                        2.4,
                        2.4,
                        2.4,
                    ],
                    'multiapp_coef': 1,
                    'price_bucket': [
                        50,
                        100,
                        150,
                        200,
                        250,
                        300,
                        350,
                        400,
                        450,
                        500,
                        550,
                        600,
                        650,
                    ],
                },
                '3': {
                    'elasticity': [
                        2.9,
                        2.9,
                        2.9,
                        2.9,
                        3.2,
                        3.2,
                        3.2,
                        3.2,
                        3.2,
                        3.2,
                        3.5,
                        3.5,
                        3.5,
                    ],
                    'multiapp_coef': 1,
                    'price_bucket': [
                        50,
                        100,
                        150,
                        200,
                        250,
                        300,
                        350,
                        400,
                        450,
                        500,
                        550,
                        600,
                        650,
                    ],
                },
                'random': {
                    'elasticity': [
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                        0.8,
                    ],
                    'multiapp_coef': 1,
                    'price_bucket': [
                        50,
                        100,
                        150,
                        200,
                        250,
                        300,
                        350,
                        400,
                        450,
                        500,
                        550,
                        600,
                        650,
                    ],
                },
            },
        },
    },
}

DISCOUNT_INFO = {
    'discount_id': '3670',
    'series_id': 'dd8f47467f7541d8813db274926dde98',
    'hierarchy_name': 'full_money_discounts',
    'meta_info': {
        'create_draft_id': '276031',
        'create_tickets': ['RUPRICING-7246'],
        'create_multidraft_id': '276037',
    },
    'rules': [
        {'condition_name': 'intermediate_point_is_set', 'values': 'Other'},
        {'condition_name': 'class', 'values': ['katusha']},
        {
            'condition_name': 'zone',
            'values': [
                {
                    'name': 'kazan',
                    'type': 'tariff_zone',
                    'is_prioritized': False,
                },
            ],
        },
        {'condition_name': 'order_type', 'values': 'Other'},
        {'condition_name': 'tag_from_experiment', 'values': 'Other'},
        {'condition_name': 'tag', 'values': ['kt2_random']},
        {'condition_name': 'payment_method', 'values': ['card', 'applepay']},
        {'condition_name': 'application_brand', 'values': 'Other'},
        {'condition_name': 'application_platform', 'values': 'Other'},
        {'condition_name': 'application_type', 'values': 'Other'},
        {'condition_name': 'has_yaplus', 'values': 'Other'},
        {
            'condition_name': 'tariff',
            'values': ['econom', 'uberx', 'business'],
        },
        {'condition_name': 'point_b_is_set', 'values': [1]},
        {'condition_name': 'geoarea_a_set', 'values': [[]]},
        {'condition_name': 'geoarea_b_set', 'values': [[]]},
        {
            'condition_name': 'surge_range',
            'values': [{'start': '0.000000', 'end': '1.200000'}],
        },
        {
            'condition_name': 'active_period',
            'values': [
                {
                    'start': '2021-10-11T15:23:34+03:00',
                    'end': '2022-10-11T15:23:34+03:00',
                    'is_start_utc': True,
                    'is_end_utc': True,
                },
            ],
        },
    ],
    'discount': {
        'name': 'kt2_random',
        'values_with_schedules': [
            {
                'schedule': {
                    'timezone': 'LOCAL',
                    'intervals': [
                        {'exclude': False, 'day': [1, 2, 3, 4, 5, 6, 7]},
                    ],
                },
                'money_value': {
                    'discount_value': {
                        'value_type': 'table',
                        'value': [
                            {'from_cost': 50.0, 'discount': 12.0},
                            {'from_cost': 100.0, 'discount': 12.0},
                            {'from_cost': 150.0, 'discount': 12.0},
                            {'from_cost': 200.0, 'discount': 12.0},
                            {'from_cost': 250.0, 'discount': 12.0},
                            {'from_cost': 300.0, 'discount': 12.0},
                            {'from_cost': 350.0, 'discount': 12.0},
                            {'from_cost': 400.0, 'discount': 12.0},
                            {'from_cost': 450.0, 'discount': 12.0},
                            {'from_cost': 500.0, 'discount': 12.0},
                            {'from_cost': 550.0, 'discount': 12.0},
                            {'from_cost': 600.0, 'discount': 9.0},
                            {'from_cost': 650.0, 'discount': 6.0},
                            {'from_cost': 700.0, 'discount': 0.0},
                        ],
                    },
                    'max_absolute_value': 300.0,
                },
            },
        ],
        'description': 'kt2_random',
        'limits': {
            'id': 'discount_kt2_cdc9329e-82c7-4482-9edd-321bea0f5e8b',
            'daily_limit': {'value': '1472909', 'threshold': 100},
            'weekly_limit': {
                'value': '10310364',
                'threshold': 100,
                'type': 'sliding',
            },
        },
    },
}

FIND_DISCOUNTS_INFO = {
    'discounts_data': {
        'hierarchy_name': 'full_money_discounts',
        'discounts_info': [
            {
                'discount_id': '3670',
                'name': 'kt2_random',
                'create_draft_id': '276031',
                'conditions': [
                    {
                        'condition_name': 'active_period',
                        'values': [
                            {
                                'start': '2021-10-11T15:23:34+03:00',
                                'end': '2022-10-11T15:23:34+03:00',
                                'is_start_utc': True,
                                'is_end_utc': True,
                            },
                        ],
                    },
                    {
                        'condition_name': 'zone',
                        'values': [
                            {
                                'name': 'kazan',
                                'type': 'tariff_zone',
                                'is_prioritized': False,
                            },
                        ],
                    },
                    {'condition_name': 'class', 'values': ['katusha']},
                    {
                        'condition_name': 'tariff',
                        'values': ['econom', 'uberx', 'business'],
                    },
                    {'condition_name': 'tag', 'values': ['kt2_random']},
                ],
            },
        ],
    },
}

MULTIDRAFT_ID = 42


@pytest.fixture
async def mock_other_services(
        patch,
        mock_ride_discounts,
        mock_taxi_approvals,
        mock_atlas_backend,
        mockserver,
        load_json,
):
    @mock_ride_discounts('/v1/admin/match-discounts/find-discounts')
    async def _find_discounts(request):
        return FIND_DISCOUNTS_INFO

    @mock_ride_discounts('/v1/admin/match-discounts/load-discount')
    async def _load_discount(request):
        return DISCOUNT_INFO

    @mockserver.json_handler('/startrek/issues')
    async def _create_ticket(*args, **kwargs):
        return {'key': 'TESTQUEUE-1'}

    @mock_taxi_approvals('/drafts/create/')
    async def _create_draft_handler(request):
        return {'id': 1, 'version': 1, 'status': 'waiting_check'}

    @mock_taxi_approvals('/drafts/attach/')
    async def _attach_draft_handler(request):
        return {'id': 1, 'version': 1}

    @mock_taxi_approvals('/drafts/1/')
    async def _get_draft_handler(request):
        return {'id': 1, 'version': 2, 'status': 'need_approval'}

    @mock_taxi_approvals('/multidrafts/create/')
    async def _create_multidraft_handler(request):
        if 'Москва' in request.json['description']:
            multidraft_id = MULTIDRAFT_ID
        elif 'Нижний Тагил' in request.json['description']:
            multidraft_id = MULTIDRAFT_ID + 100
        elif 'Санкт-Петербург' in request.json['description']:
            multidraft_id = MULTIDRAFT_ID + 200
        elif 'Казань' in request.json['description']:
            multidraft_id = MULTIDRAFT_ID + 300
        else:
            raise RuntimeError('Unknown city!')

        return {
            'id': multidraft_id,
            'created_by': 'artem-mazanov',
            'created': '2021-10-28T14:04:33+0300',
            'updated': '2021-10-28T14:04:33+0300',
            'version': 1,
            'comments': [
                {
                    'login': 'artem-mazanov',
                    'comment': 'artem-mazanov прикрепил тикет TESTQUEUE-1',
                },
            ],
            'description': 'Выключение скидок в городе Москва',
            'tickets': ['TESTQUEUE-1'],
            'status': 'need_approval',
            'data': {},
        }

    @mock_atlas_backend('/api/classes')
    async def atlas_backend_handler_classes(request):  # pylint: disable=W0612
        return web.json_response(
            [{'ru': 'Эконом', 'en': 'econom'}, {'ru': 'uberX', 'en': 'uberx'}],
        )


@pytest.fixture(scope='function')
def mock_active_discounts(monkeypatch):
    creation_lags = {'test_city': 100, 'test_city_push': 50}

    async def retrieve_active_discounts(cls, ctx, *_):
        return cls(ctx, [])

    def is_active_discounts_with_push(_, city):
        return city == 'test_city_push'

    def get_creation_lag(_, city: str):
        return creation_lags[city]

    monkeypatch.setattr(
        helpers.ActiveDiscounts,
        'retrieve_active_discounts',
        classmethod(retrieve_active_discounts),
    )

    monkeypatch.setattr(
        helpers.ActiveDiscounts, 'get_creation_lag', get_creation_lag,
    )

    monkeypatch.setattr(
        helpers.ActiveDiscounts,
        'is_active_discounts_with_push',
        is_active_discounts_with_push,
    )
    yield


@pytest.fixture(scope='function')
def set_segments_stats_suggest(pgsql):
    def inner(suggest_id):
        cursor = pgsql['discounts_operation_calculations'].cursor()
        # change suggest_id for segment_stats
        query = f"""
            UPDATE discounts_operation_calculations.segment_stats_all
            SET suggest_id = {suggest_id}
        """
        cursor.execute(query)
        cursor.close()

    return inner

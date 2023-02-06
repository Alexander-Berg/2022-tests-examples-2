import pytest

from taxi_dispatch_logs_admin.api.common import helpers
from taxi_dispatch_logs_admin.api.common import request_logs_logic
from taxi_dispatch_logs_admin.generated.service.swagger import models

_DUMMY_PARAMS = {
    'draw_id': 'draw_id_0',
    'from_dt': '2020-01-01T00:00:00+03:00',
    'to_dt': '2020-01-01T00:00:00+03:00',
}


_EDGE_1_META = {'rd': 1.1, 'rt': 1.2, 'score': 1.3}

_EDGE_2_META = {'rd': 2.1, 'rt': 2.2, 'score': 2.3}

_EDGE_3_META = {'rd': 3.1, 'rt': 3.2, 'score': 3.3}

_EDGE_4_META = {'rd': 4.1, 'rt': 4.2, 'score': 4.3}

_EDGE_WO_SCORE_META = {'rd': 3.1, 'rt': 3.2, 'score': None}


@pytest.mark.parametrize(
    """
        orders_logs,
        expected
    """,
    [
        (
            [
                {
                    'order_id': 'order_id_1',
                    'offer_id': 'offer_id_1',
                    'timestamp': '1592265600',
                    'geo_point': [1.0, 0.0],
                    'winner_id': 'candidate_id_2',
                    'winner_applied': True,
                    'candidates_meta': {
                        'candidate_id_1': {
                            'id': 'candidate_id_1',
                            'geo_point': [0.0, 1.0],
                            **_EDGE_1_META,
                        },
                        'candidate_id_2': {
                            'id': 'candidate_id_2',
                            'geo_point': [0.0, 2.0],
                            **_EDGE_2_META,
                        },
                    },
                    'allowed_classes': ['econom'],
                    'retention_score': 2.2,
                },
            ],
            {
                'orders': {
                    'order_id_1': {
                        'candidates': {
                            'candidate_id_1': {
                                'id': 'candidate_id_1',
                                'geo_point': [0.0, 1.0],
                                **_EDGE_1_META,
                                'winner': False,
                                'winner_applied': False,
                            },
                            'candidate_id_2': {
                                'id': 'candidate_id_2',
                                'geo_point': [0.0, 2.0],
                                **_EDGE_2_META,
                                'winner': True,
                                'winner_applied': True,
                            },
                        },
                        'stats': {
                            'geo_point': [1.0, 0.0],
                            'candidates_count': 2,
                        },
                        'retention_score': 2.2,
                        'allowed_classes': ['econom'],
                    },
                },
                'offers': {},
                'candidates': {
                    'candidate_id_1': {
                        'orders': {
                            'order_id_1': {
                                'id': 'order_id_1',
                                'geo_point': [1.0, 0.0],
                                **_EDGE_1_META,
                                'winner': False,
                                'winner_applied': False,
                            },
                        },
                        'offers': {},
                        'stats': {
                            'geo_point': [0.0, 1.0],
                            'orders_offers_count': 1,
                        },
                    },
                    'candidate_id_2': {
                        'orders': {
                            'order_id_1': {
                                'id': 'order_id_1',
                                'geo_point': [1.0, 0.0],
                                **_EDGE_2_META,
                                'winner': True,
                                'winner_applied': True,
                            },
                        },
                        'offers': {},
                        'stats': {
                            'geo_point': [0.0, 2.0],
                            'orders_offers_count': 1,
                        },
                    },
                },
                'agg_stats': {
                    'dttm': '2020-06-16T03:00:00+03:00',
                    'orders_offers_count': 1,
                    'candidates_count': 2,
                    'solved_count': 1,
                    'orders_offers_hist': {'1': 2},
                    'candidates_hist': {'2': 1},
                },
            },
        ),
        (
            [
                {
                    'order_id': 'order_id_1',
                    'offer_id': 'offer_id_1',
                    'timestamp': '1592265600',
                    'geo_point': [1.0, 0.0],
                    'winner_id': 'candidate_id_1',
                    'winner_applied': False,
                    'candidates_meta': {
                        'candidate_id_1': {
                            'id': 'candidate_id_1',
                            'geo_point': [0.0, 1.0],
                            **_EDGE_1_META,
                        },
                        'candidate_id_2': {
                            'id': 'candidate_id_2',
                            'geo_point': [0.0, 2.0],
                            **_EDGE_2_META,
                        },
                    },
                    'retention_score': None,
                    'allowed_classes': None,
                },
                {
                    'order_id': None,
                    'offer_id': 'offer_id_2',
                    'timestamp': '1592265600',
                    'geo_point': [2.0, 0.0],
                    'winner_id': 'candidate_id_2',
                    'winner_applied': True,
                    'candidates_meta': {
                        'candidate_id_1': {
                            'id': 'candidate_id_1',
                            'geo_point': [0.0, 1.0],
                            **_EDGE_3_META,
                        },
                        'candidate_id_2': {
                            'id': 'candidate_id_2',
                            'geo_point': [0.0, 2.0],
                            **_EDGE_4_META,
                        },
                        'candidate_id_3': {
                            'id': 'candidate_id_3',
                            'geo_point': [0.0, 3.0],
                            **_EDGE_WO_SCORE_META,
                        },
                    },
                    'retention_score': 0,
                    'allowed_classes': ['econom', 'business'],
                },
                {
                    'order_id': 'order_id_3',
                    'offer_id': 'offer_id_3',
                    'timestamp': '1592265600',
                    'geo_point': [3.0, 0.0],
                    'winner_id': None,
                    'winner_applied': False,
                    'candidates_meta': {},
                    'retention_score': None,
                    'allowed_classes': None,
                },
            ],
            {
                'orders': {
                    'order_id_1': {
                        'candidates': {
                            'candidate_id_1': {
                                'id': 'candidate_id_1',
                                'geo_point': [0.0, 1.0],
                                **_EDGE_1_META,
                                'winner': True,
                                'winner_applied': False,
                            },
                            'candidate_id_2': {
                                'id': 'candidate_id_2',
                                'geo_point': [0.0, 2.0],
                                **_EDGE_2_META,
                                'winner': False,
                                'winner_applied': False,
                            },
                        },
                        'stats': {
                            'geo_point': [1.0, 0.0],
                            'candidates_count': 2,
                        },
                    },
                    'order_id_3': {
                        'candidates': {},
                        'stats': {
                            'geo_point': [3.0, 0.0],
                            'candidates_count': 0,
                        },
                    },
                },
                'offers': {
                    'offer_id_2': {
                        'candidates': {
                            'candidate_id_1': {
                                'id': 'candidate_id_1',
                                'geo_point': [0.0, 1.0],
                                **_EDGE_3_META,
                                'winner': False,
                                'winner_applied': False,
                            },
                            'candidate_id_2': {
                                'id': 'candidate_id_2',
                                'geo_point': [0.0, 2.0],
                                **_EDGE_4_META,
                                'winner': True,
                                'winner_applied': True,
                            },
                        },
                        'stats': {
                            'geo_point': [2.0, 0.0],
                            'candidates_count': 2,
                        },
                        'retention_score': 0,
                        'allowed_classes': ['econom', 'business'],
                    },
                },
                'candidates': {
                    'candidate_id_1': {
                        'orders': {
                            'order_id_1': {
                                'id': 'order_id_1',
                                'geo_point': [1.0, 0.0],
                                **_EDGE_1_META,
                                'winner': True,
                                'winner_applied': False,
                            },
                        },
                        'offers': {
                            'offer_id_2': {
                                'id': 'offer_id_2',
                                'geo_point': [2.0, 0.0],
                                **_EDGE_3_META,
                                'winner': False,
                                'winner_applied': False,
                            },
                        },
                        'stats': {
                            'geo_point': [0.0, 1.0],
                            'orders_offers_count': 2,
                        },
                    },
                    'candidate_id_2': {
                        'orders': {
                            'order_id_1': {
                                'id': 'order_id_1',
                                'geo_point': [1.0, 0.0],
                                **_EDGE_2_META,
                                'winner': False,
                                'winner_applied': False,
                            },
                        },
                        'offers': {
                            'offer_id_2': {
                                'id': 'offer_id_2',
                                'geo_point': [2.0, 0.0],
                                **_EDGE_4_META,
                                'winner': True,
                                'winner_applied': True,
                            },
                        },
                        'stats': {
                            'geo_point': [0.0, 2.0],
                            'orders_offers_count': 2,
                        },
                    },
                },
                'agg_stats': {
                    'dttm': '2020-06-16T03:00:00+03:00',
                    'orders_offers_count': 3,
                    'candidates_count': 2,
                    'solved_count': 1,
                    'orders_offers_hist': {'2': 2},
                    'candidates_hist': {'0': 1, '2': 2},
                },
            },
        ),
    ],
)
async def test_draw_desc(web_app_client, monkeypatch, orders_logs, expected):
    async def _dummy_fetch_task_record(*args, **kwargs):
        return {'status': 'completed', 'yt_results': 'yt_results'}

    monkeypatch.setattr(
        request_logs_logic, 'fetch_task_record', _dummy_fetch_task_record,
    )

    def _dummy_is_record_schedulable(*args, **kwargs):
        return False

    monkeypatch.setattr(
        helpers, 'is_record_schedulable', _dummy_is_record_schedulable,
    )

    async def _dummy_fetch_logs(*args, **kwargs):
        log_items = [
            models.api.DispatchBufferLogItem(order_log=order_log, draw_log={})
            for order_log in orders_logs
        ]
        return models.api.LogsResponse(
            log_type='dispatch_buffer', dispatch_buffer_logs=log_items,
        )

    monkeypatch.setattr(request_logs_logic, 'fetch_logs', _dummy_fetch_logs)

    response = await web_app_client.post('/draw_desc/', params=_DUMMY_PARAMS)
    assert response.status == 200
    content = await response.json()
    assert content == {'draw_id': _DUMMY_PARAMS['draw_id'], **expected}

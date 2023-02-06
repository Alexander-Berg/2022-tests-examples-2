import pytest

from . import utils_v2

JOB_NAME = 'cargo-claims-status-monitor'

CARGO_MAIN_BOARD_SETTINGS = {
    'statistics_ttl_seconds': 180,
    'non_terminal_statuses_hanged_count': {
        'settings': {
            'enabled': True,
            'delayed_orders_start_lookup_shift_seconds': 360,
        },
        'non_terminal_statuses_hanged_durations': {
            'new': 100,
            'estimating': 100,
            'estimating_failed': 100,
            'ready_for_approval': 100,
            '[real_lookup_soon]': 100,
            '[real_lookup_delayed]': 100,
            'accepted': 100,
            'performer_lookup': 100,
            'performer_draft': 100,
            'performer_draft_delayed': 100,
            'performer_found': 100,
            'performer_not_found': 100,
            'pickup_arrived': 100,
            'ready_for_pickup_confirmation': 100,
            'pickuped': 100,
            'delivery_arrived': 100,
            'ready_for_delivery_confirmation': 100,
            'pay_waiting': 100,
            'delivered': 100,
            'returning': 100,
            'return_arrived': 100,
            'ready_for_return_confirmation': 100,
            'returned': 100,
            'some_status': 2147483647,
        },
    },
    'increments': {
        'enabled': True,
        'left_boundary_shift_seconds': 60,
        'right_boundary_shift_seconds': 0,
    },
    'empty_is_delayed_field_count': {
        'enabled': True,
        'left_boundary_shift_seconds': 60,
        'right_boundary_shift_seconds': 0,
    },
    'found_share': {
        'enabled': True,
        'left_boundary_shift_seconds': 60,
        'right_boundary_shift_seconds': 0,
    },
    'accepted_share': {
        'enabled': True,
        'left_boundary_shift_seconds': 60,
        'right_boundary_shift_seconds': 0,
    },
    'accepted_rate_vs_completion_rate': {
        'enabled': True,
        'left_boundary_shift_seconds': 60,
        'right_boundary_shift_seconds': 0,
    },
    'burn_rate': {
        'enabled': True,
        'left_boundary_shift_seconds': 60,
        'right_boundary_shift_seconds': 0,
    },
    'accepted_rate_vs_completion_rate_delayed': {
        'enabled': True,
        'left_boundary_shift_seconds': 60,
        'right_boundary_shift_seconds': 0,
    },
    'burn_rate_delayed': {
        'enabled': True,
        'left_boundary_shift_seconds': 60,
        'right_boundary_shift_seconds': 0,
    },
    'found_share_delayed': {
        'enabled': True,
        'left_boundary_shift_seconds': 60,
        'right_boundary_shift_seconds': 0,
    },
    'pinpoint_target_dashboards': [
        {
            'name': 'my_pinpoint_target_dashboards',
            'zones': ['ekb'],
            'corp_clients': ['01234567890123456789012345678912'],
        },
    ],
    'phoenix': {'enabled': True, 'left_boundary_shift_seconds': 1000},
}


def get_config(enabled):
    config = {'enabled': enabled, 'query-limit': 1000, 'sleep-time-ms': 1}
    return config


async def wait_iteration(taxi_cargo_claims, testpoint):
    @testpoint(JOB_NAME + '-finished')
    def finished(data):
        return data

    async with taxi_cargo_claims.spawn_task(JOB_NAME):
        finished = await finished.wait_call()
        return finished['data']


@pytest.mark.config(
    CARGO_CLAIMS_STATUS_MONITOR_WORKMODE=get_config(True),
    CARGO_MAIN_BOARD_SETTINGS=CARGO_MAIN_BOARD_SETTINGS,
)
async def test_worker_empty(taxi_cargo_claims, testpoint):
    stats = await wait_iteration(taxi_cargo_claims, testpoint)
    assert 'phoenix' in stats
    stats.pop('phoenix')
    assert stats == {
        'status_transitions': {
            'accepted_share': {'new': 0, 'accepted': 0},
            'found_share': {'accepted': 0, 'found': 0},
            'accepted_rate_vs_completion_rate': {
                'accepted': 0,
                'completed': 0,
            },
            'burn_rate': {'accepted': 0, 'burnt': 0},
            'found_share_delayed': {'accepted': 0, 'found': 0},
            'accepted_rate_vs_completion_rate_delayed': {
                'accepted': 0,
                'completed': 0,
            },
            'burn_rate_delayed': {'accepted': 0, 'burnt': 0},
        },
        't_i': {
            'i': {
                'accepted': 0.0,
                'delivered_finish': 0.0,
                'pickuped': 0.0,
                'new': 0.0,
                'cancelled': 0.0,
                'cancelled_by_taxi': 0.0,
                'cancelled_with_items_on_hands': 0.0,
                'cancelled_with_payment': 0.0,
                'delivered': 0.0,
                'delivery_arrived': 0.0,
                'estimating': 0.0,
                'estimating_failed': 0.0,
                'failed': 0.0,
                'pay_waiting': 0.0,
                'performer_draft': 0.0,
                'performer_found': 0.0,
                'performer_lookup': 0.0,
                'performer_not_found': 0.0,
                'pickup_arrived': 0.0,
                'ready_for_approval': 0.0,
                'ready_for_delivery_confirmation': 0.0,
                'ready_for_pickup_confirmation': 0.0,
                'ready_for_return_confirmation': 0.0,
                'return_arrived': 0.0,
                'returned': 0.0,
                'returned_finish': 0.0,
                'returning': 0.0,
            },
        },
        'hanged': {},
        'zero_errors': {
            'graphs_plotting_errors_count': 0.0,
            'empty_is_delayed_field_count': 0.0,
            'disabled_graphs_count': 0.0,
        },
    }


@pytest.mark.config(
    CARGO_CLAIMS_STATUS_MONITOR_WORKMODE=get_config(True),
    CARGO_MAIN_BOARD_SETTINGS={
        'metrics_thresholds': {
            'graphs_plotting_errors_count': {'min_value': 3},
        },
    },
)
async def test_thresholds1(taxi_cargo_claims, testpoint, create_default_claim):
    stats = await wait_iteration(taxi_cargo_claims, testpoint)
    assert stats['zero_errors']['graphs_plotting_errors_count'] == 19


@pytest.mark.config(
    CARGO_CLAIMS_STATUS_MONITOR_WORKMODE=get_config(True),
    CARGO_MAIN_BOARD_SETTINGS={
        'metrics_thresholds': {
            'graphs_plotting_errors_count': {'min_value': 22},
        },
    },
)
async def test_thresholds2(taxi_cargo_claims, testpoint, create_default_claim):
    stats = await wait_iteration(taxi_cargo_claims, testpoint)
    assert stats['zero_errors']['graphs_plotting_errors_count'] == 0


@pytest.mark.config(
    CARGO_CLAIMS_STATUS_MONITOR_WORKMODE=get_config(True),
    CARGO_MAIN_BOARD_SETTINGS={
        'metrics_thresholds': {'graphs_plotting_errors_count': {}},
    },
)
async def test_thresholds3(taxi_cargo_claims, testpoint, create_default_claim):
    stats = await wait_iteration(taxi_cargo_claims, testpoint)
    assert stats['zero_errors']['graphs_plotting_errors_count'] == 19


@pytest.mark.config(
    CARGO_CLAIMS_STATUS_MONITOR_WORKMODE=get_config(True),
    CARGO_CLAIMS_CORP_CLIENT_IDS_ALIASES={
        '01234567890123456789012345678912': 'eda',
    },
    CARGO_MAIN_BOARD_SETTINGS=CARGO_MAIN_BOARD_SETTINGS,
)
async def test_worker_not_empty(
        taxi_cargo_claims, testpoint, pgsql, create_default_claim,
):
    cursor = pgsql['cargo_claims'].cursor()

    cursor.execute(
        """
            UPDATE cargo_claims.claims SET is_delayed = false;
        """,
    )
    for _ in range(5):
        cursor.execute(
            """UPDATE cargo_claims.claims SET status = 'accepted';
            """,
        )
        cursor.execute(
            """UPDATE cargo_claims.claims SET status = 'delivered_finish';
            """,
        )
    for i in [1, 2, 3]:
        cursor.execute(
            f"""
            UPDATE cargo_claims.claims
            SET status = 'pickuped', current_point = {i}, zone_id = 'ekb';
            """,
        )
    stats = await wait_iteration(taxi_cargo_claims, testpoint)

    assert 'eda' in stats
    assert 'phoenix' in stats
    stats.pop('phoenix')
    stats.pop('hanged')
    stats['eda'].pop('hanged')
    stats['ptd']['my_pinpoint_target_dashboards'].pop('hanged')
    assert stats == {
        'eda': {
            'status_transitions': {
                'accepted_share': {'new': 1.0, 'accepted': 1.0},
                'found_share': {'accepted': 1.0, 'found': 0.0},
                'accepted_rate_vs_completion_rate': {
                    'accepted': 1.0,
                    'completed': 1.0,
                },
                'burn_rate': {'accepted': 1.0, 'burnt': 0.0},
                'found_share_delayed': {'accepted': 0.0, 'found': 0.0},
                'accepted_rate_vs_completion_rate_delayed': {
                    'accepted': 0.0,
                    'completed': 0.0,
                },
                'burn_rate_delayed': {'accepted': 0.0, 'burnt': 0.0},
            },
            't_i': {
                'i': {
                    'accepted': 1.0,
                    'delivered_finish': 1.0,
                    'pickuped': 1.0,
                    'new': 1.0,
                    'cancelled': 0.0,
                    'cancelled_by_taxi': 0.0,
                    'cancelled_with_items_on_hands': 0.0,
                    'cancelled_with_payment': 0.0,
                    'delivered': 0.0,
                    'delivery_arrived': 0.0,
                    'estimating': 0.0,
                    'estimating_failed': 0.0,
                    'failed': 0.0,
                    'pay_waiting': 0.0,
                    'performer_draft': 0.0,
                    'performer_found': 0.0,
                    'performer_lookup': 0.0,
                    'performer_not_found': 0.0,
                    'pickup_arrived': 0.0,
                    'ready_for_approval': 0.0,
                    'ready_for_delivery_confirmation': 0.0,
                    'ready_for_pickup_confirmation': 0.0,
                    'ready_for_return_confirmation': 0.0,
                    'return_arrived': 0.0,
                    'returned': 0.0,
                    'returned_finish': 0.0,
                    'returning': 0.0,
                },
            },
        },
        'ptd': {
            'my_pinpoint_target_dashboards': {
                'status_transitions': {
                    'accepted_share': {'new': 1.0, 'accepted': 1.0},
                    'found_share': {'accepted': 1.0, 'found': 0.0},
                    'accepted_rate_vs_completion_rate': {
                        'accepted': 1.0,
                        'completed': 1.0,
                    },
                    'burn_rate': {'accepted': 1.0, 'burnt': 0.0},
                    'found_share_delayed': {'accepted': 0.0, 'found': 0.0},
                    'accepted_rate_vs_completion_rate_delayed': {
                        'accepted': 0.0,
                        'completed': 0.0,
                    },
                    'burn_rate_delayed': {'accepted': 0.0, 'burnt': 0.0},
                },
            },
        },
        'status_transitions': {
            'accepted_share': {'new': 1.0, 'accepted': 1.0},
            'found_share': {'accepted': 1.0, 'found': 0.0},
            'accepted_rate_vs_completion_rate': {
                'accepted': 1.0,
                'completed': 1.0,
            },
            'burn_rate': {'accepted': 1.0, 'burnt': 0.0},
            'found_share_delayed': {'accepted': 0.0, 'found': 0.0},
            'accepted_rate_vs_completion_rate_delayed': {
                'accepted': 0.0,
                'completed': 0.0,
            },
            'burn_rate_delayed': {'accepted': 0.0, 'burnt': 0.0},
        },
        't_i': {
            'i': {
                'accepted': 1.0,
                'delivered_finish': 1.0,
                'pickuped': 1.0,
                'new': 1.0,
                'cancelled': 0.0,
                'cancelled_by_taxi': 0.0,
                'cancelled_with_items_on_hands': 0.0,
                'cancelled_with_payment': 0.0,
                'delivered': 0.0,
                'delivery_arrived': 0.0,
                'estimating': 0.0,
                'estimating_failed': 0.0,
                'failed': 0.0,
                'pay_waiting': 0.0,
                'performer_draft': 0.0,
                'performer_found': 0.0,
                'performer_lookup': 0.0,
                'performer_not_found': 0.0,
                'pickup_arrived': 0.0,
                'ready_for_approval': 0.0,
                'ready_for_delivery_confirmation': 0.0,
                'ready_for_pickup_confirmation': 0.0,
                'ready_for_return_confirmation': 0.0,
                'return_arrived': 0.0,
                'returned': 0.0,
                'returned_finish': 0.0,
                'returning': 0.0,
            },
        },
        'zero_errors': {
            'graphs_plotting_errors_count': 0.0,
            'empty_is_delayed_field_count': 0.0,
            'disabled_graphs_count': 0.0,
        },
    }


@pytest.mark.config(
    CARGO_CLAIMS_STATUS_MONITOR_WORKMODE=get_config(True),
    CARGO_MAIN_BOARD_SETTINGS=CARGO_MAIN_BOARD_SETTINGS,
)
async def test_worker_for_phoenix(
        taxi_cargo_claims, testpoint, pgsql, mock_cargo_corp_up,
):
    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims, is_phoenix_corp=True,
    )
    assert response.status_code == 200
    response, _ = await utils_v2.create_claim_v2(
        taxi_cargo_claims,
        request_id='1234',
        corp_client_id='1234567890abcdef1234567890abcdef',
    )
    assert response.status_code == 200

    cursor = pgsql['cargo_claims'].cursor()

    cursor.execute(
        """
            UPDATE cargo_claims.claims SET is_delayed = false,
            created_ts = now() - '2 minutes'::INTERVAL;
        """,
    )
    cursor.execute(
        """UPDATE cargo_claims.claims SET status = 'accepted';
        """,
    )
    cursor.execute(
        """UPDATE cargo_claims.claims SET status = 'delivered_finish';
        """,
    )
    cursor.execute(
        f"""
        UPDATE cargo_claims.claims
        SET status = 'pickuped';
        """,
    )
    cursor.execute(
        """
            UPDATE cargo_claims.claims SET
            last_status_change_ts = current_timestamp - '5 minutes'::INTERVAL;
        """,
    )
    stats = await wait_iteration(taxi_cargo_claims, testpoint)

    assert 'phoenix' in stats
    assert stats == {
        'phoenix': {
            'status_transitions': {
                'accepted_share': {'new': 1.0, 'accepted': 1.0},
                'found_share': {'accepted': 1.0, 'found': 0.0},
                'accepted_rate_vs_completion_rate': {
                    'accepted': 1.0,
                    'completed': 1.0,
                },
                'burn_rate': {'accepted': 1.0, 'burnt': 0.0},
                'found_share_delayed': {'accepted': 0.0, 'found': 0.0},
                'accepted_rate_vs_completion_rate_delayed': {
                    'accepted': 0.0,
                    'completed': 0.0,
                },
                'burn_rate_delayed': {'accepted': 0.0, 'burnt': 0.0},
            },
            't_i': {
                'i': {
                    'accepted': 1.0,
                    'delivered_finish': 1.0,
                    'pickuped': 1.0,
                    'new': 1.0,
                    'cancelled': 0.0,
                    'cancelled_by_taxi': 0.0,
                    'cancelled_with_items_on_hands': 0.0,
                    'cancelled_with_payment': 0.0,
                    'delivered': 0.0,
                    'delivery_arrived': 0.0,
                    'estimating': 0.0,
                    'estimating_failed': 0.0,
                    'failed': 0.0,
                    'pay_waiting': 0.0,
                    'performer_draft': 0.0,
                    'performer_found': 0.0,
                    'performer_lookup': 0.0,
                    'performer_not_found': 0.0,
                    'pickup_arrived': 0.0,
                    'ready_for_approval': 0.0,
                    'ready_for_delivery_confirmation': 0.0,
                    'ready_for_pickup_confirmation': 0.0,
                    'ready_for_return_confirmation': 0.0,
                    'return_arrived': 0.0,
                    'returned': 0.0,
                    'returned_finish': 0.0,
                    'returning': 0.0,
                },
            },
            'hanged': {'pickuped': 1.0},
        },
        'status_transitions': {
            'accepted_share': {'new': 2.0, 'accepted': 2.0},
            'found_share': {'accepted': 2.0, 'found': 0.0},
            'accepted_rate_vs_completion_rate': {
                'accepted': 2.0,
                'completed': 2.0,
            },
            'burn_rate': {'accepted': 2.0, 'burnt': 0.0},
            'found_share_delayed': {'accepted': 0.0, 'found': 0.0},
            'accepted_rate_vs_completion_rate_delayed': {
                'accepted': 0.0,
                'completed': 0.0,
            },
            'burn_rate_delayed': {'accepted': 0.0, 'burnt': 0.0},
        },
        't_i': {
            'i': {
                'accepted': 2.0,
                'delivered_finish': 2.0,
                'pickuped': 2.0,
                'new': 2.0,
                'cancelled': 0.0,
                'cancelled_by_taxi': 0.0,
                'cancelled_with_items_on_hands': 0.0,
                'cancelled_with_payment': 0.0,
                'delivered': 0.0,
                'delivery_arrived': 0.0,
                'estimating': 0.0,
                'estimating_failed': 0.0,
                'failed': 0.0,
                'pay_waiting': 0.0,
                'performer_draft': 0.0,
                'performer_found': 0.0,
                'performer_lookup': 0.0,
                'performer_not_found': 0.0,
                'pickup_arrived': 0.0,
                'ready_for_approval': 0.0,
                'ready_for_delivery_confirmation': 0.0,
                'ready_for_pickup_confirmation': 0.0,
                'ready_for_return_confirmation': 0.0,
                'return_arrived': 0.0,
                'returned': 0.0,
                'returned_finish': 0.0,
                'returning': 0.0,
            },
        },
        'zero_errors': {
            'graphs_plotting_errors_count': 0.0,
            'empty_is_delayed_field_count': 0.0,
            'disabled_graphs_count': 0.0,
        },
        'hanged': {'pickuped': 2.0},
    }

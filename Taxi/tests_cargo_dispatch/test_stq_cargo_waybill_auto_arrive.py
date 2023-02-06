import datetime
import uuid

import pytest

from testsuite.utils import matching

# FALLBACK_ROUTER = 'fallback_router'

ARRIVE_SETTINGS_EXPERIMENT_NAME = (
    'cargo_dispatch_stq_cargo_alive_batch_confirmation_arrive_settings'
)

ARRIVE_SETTINGS_CONSUMER_NAME = (
    'cargo_dispatch/stq-cargo-alive-batch-confirmation-arrive-settings'
)

MOCK_TIME = '2021-01-01T00:00:00+00:00'
CARGO_ARRIVE_AT_POINT_DELAY = datetime.timedelta(seconds=5)
CARGO_ARRIVE_AT_POINT_DELAY_MILLISECONDS = (
    CARGO_ARRIVE_AT_POINT_DELAY.total_seconds() * 1000
)

MOCK_TIME_EXPECTED_ETA = (
    datetime.datetime.fromisoformat(MOCK_TIME) + CARGO_ARRIVE_AT_POINT_DELAY
).replace(tzinfo=None)


class MatchEachOnce:
    """Matches each object of specified list only once
    """

    def __init__(self, items: list):
        self.source_items = set(items)
        self.matched_items = set()  # type: ignore

    def __repr__(self):
        return '<MatchEachOnce>' + str(self.source_items)

    def __eq__(self, item):
        if item in self.source_items and item not in self.matched_items:
            self.matched_items.add(item)
            return True
        return False

    def is_all_matched(self):
        return self.matched_items == self.source_items


@pytest.mark.now(MOCK_TIME)
async def test_claim_arrive_calls(
        stq, stq_runner, mock_claims_arrive_at_point,
):
    segment_points = [
        {'claim_point_id': 11, 'segment_id': 'seg1'},
        {'claim_point_id': 12, 'segment_id': 'seg1'},
        {'claim_point_id': 41, 'segment_id': 'seg4'},
    ]
    point_id_matcher = MatchEachOnce(
        [sp['claim_point_id'] for sp in segment_points],
    )

    arrive_at_point_handler = mock_claims_arrive_at_point(
        expected_request={
            'cargo_order_id': matching.AnyString(),
            'driver': {
                'driver_profile_id': 'driver_id_1',
                'park_id': 'park_id_1',
            },
            'point_id': point_id_matcher,
        },
    )

    cargo_order_id = str(uuid.uuid4())
    expected_kwargs = {
        'cargo_order_id': cargo_order_id,
        'performer_info': {'driver_id': 'driver_id_1', 'park_id': 'park_id_1'},
        'segment_points': segment_points,
    }

    task_id = 'cargo_arrive_at_point_id'

    stq.cargo_waybill_auto_arrive.flush()
    await stq_runner.cargo_waybill_auto_arrive.call(
        task_id=task_id, kwargs=expected_kwargs,
    )

    assert point_id_matcher.is_all_matched()
    assert arrive_at_point_handler.times_called == len(
        point_id_matcher.source_items,
    )

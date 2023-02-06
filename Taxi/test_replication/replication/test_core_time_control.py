import datetime

import pytest

from replication.foundation import consts
from replication.foundation import iteration
from replication.replication.core import time_control


# pylint: disable=protected-access
@pytest.mark.parametrize(
    'start,finish,bounds_sequence,iteration_type',
    [
        (
            datetime.datetime(2018, 10, 1, 12, 10),
            datetime.datetime(2018, 10, 1, 12, 50),
            [
                {
                    'expected': [
                        datetime.datetime(2018, 10, 1, 12, 9),
                        datetime.datetime(2018, 10, 1, 12, 19),
                    ],
                    'to_update': datetime.datetime(2018, 10, 1, 12, 11),
                },
                {
                    'expected': [
                        datetime.datetime(2018, 10, 1, 12, 11),
                        datetime.datetime(2018, 10, 1, 12, 21),
                    ],
                    'to_update': datetime.datetime(2018, 10, 1, 12, 11),
                },
                {
                    'expected': [
                        datetime.datetime(2018, 10, 1, 12, 11),
                        datetime.datetime(2018, 10, 1, 12, 31),  # expand
                    ],
                    'to_update': datetime.datetime(2018, 10, 1, 12, 31),
                },
                {
                    'expected': [
                        datetime.datetime(2018, 10, 1, 12, 31),
                        datetime.datetime(2018, 10, 1, 12, 41),
                    ],
                    'to_update': datetime.datetime(2018, 10, 1, 12, 40, 30),
                },
                {
                    'expected': [
                        datetime.datetime(2018, 10, 1, 12, 40, 30),
                        datetime.datetime(2018, 10, 1, 12, 51),
                    ],
                    'to_update': datetime.datetime(2018, 10, 1, 12, 50),
                },
            ],
            consts.IterationType.MOVING_BOUNDARIES,
        ),
        (
            datetime.datetime(2018, 10, 1, 12, 10),
            datetime.datetime(2018, 10, 1, 12, 24, 20),
            [
                {
                    'expected': [
                        datetime.datetime(2018, 10, 1, 12, 9),
                        datetime.datetime(2018, 10, 1, 12, 19),
                    ],
                    'to_update': datetime.datetime(2018, 10, 1, 12, 19),
                },
                {
                    'expected': [
                        datetime.datetime(2018, 10, 1, 12, 19),
                        datetime.datetime(2018, 10, 1, 12, 25, 20),
                    ],
                    'to_update': datetime.datetime(2018, 10, 1, 12, 19),
                },
            ],
            consts.IterationType.MOVING_BOUNDARIES,
        ),
        (
            1,
            20,
            [
                {'expected': [1, 20], 'to_update': 2},
                {'expected': [2, 20], 'to_update': 20},
            ],
            consts.IterationType.CONSTANT_UPPER_BOUND_AND_STRICT_EDGES,
        ),
    ],
)
@pytest.mark.nofilldb
async def test_time_bounds_control(
        start, finish, bounds_sequence, iteration_type,
):
    controller = time_control.BoundsControl(
        _fake_source(iteration_type),
        start,
        finish,
        datetime.timedelta(seconds=60),
        datetime.timedelta(seconds=60),
    )

    current_iter_num = 0

    assert controller._active
    assert controller._bounds_updated

    for current_left, current_right in controller:
        assert current_iter_num < len(bounds_sequence)
        bounds_state = bounds_sequence[current_iter_num]
        assert [current_left, current_right] == bounds_state['expected']

        assert not controller._bounds_updated
        await controller.update_bounds(bounds_state['to_update'])
        assert controller._bounds_updated

        current_iter_num += 1

    assert not controller._active
    assert controller._bounds_updated
    assert current_iter_num == len(bounds_sequence)


@pytest.mark.nofilldb
async def test_time_ctl_simple(_fake_controller):
    for _, _ in _fake_controller:
        await _fake_controller.update_bounds(None)
    assert _fake_controller.iterations == 3


@pytest.mark.nofilldb
async def test_strict_edges():
    ctl = time_control.BoundsControl(
        _fake_source(
            consts.IterationType.CONSTANT_UPPER_BOUND_AND_STRICT_EDGES,
        ),
        1,
        20,
    )
    count = 0
    for _, _ in ctl:
        if count == 0:
            await ctl.update_bounds(2)
        else:
            with pytest.raises(time_control.UpdateBoundsError):
                await ctl.update_bounds(2)
            break
        count += 1
    assert count == 1


# pylint: disable=invalid-name
@pytest.mark.parametrize(
    'ts_to_update',
    [
        datetime.datetime(2018, 10, 1, 12, 31),
        datetime.datetime(2018, 10, 1, 12, 21),
    ],
)
@pytest.mark.nofilldb
async def test_time_ctl_fail_with_update_bounds(
        _fake_controller, ts_to_update,
):
    for _, _ in _fake_controller:
        with pytest.raises(time_control.UpdateBoundsError):
            await _fake_controller.update_bounds(ts_to_update)
        break


@pytest.mark.nofilldb
async def test_time_ctl_fail_with_double_update(_fake_controller):
    for _, _ in _fake_controller:
        await _fake_controller.update_bounds(None)
        with pytest.raises(time_control.IncorrectUsageError):
            await _fake_controller.update_bounds(None)
        break
    assert _fake_controller.iterations == 1


@pytest.mark.nofilldb
async def test_time_ctl_fail_with_no_update(_fake_controller):
    with pytest.raises(time_control.IncorrectUsageError):
        for _, _ in _fake_controller:
            pass
    assert _fake_controller.iterations == 1


@pytest.mark.nofilldb
async def test_time_ctl_fail_with_restart(_fake_controller):
    for current_left, _ in _fake_controller:
        await _fake_controller.update_bounds(current_left)

    assert _fake_controller.iterations == 3

    with pytest.raises(time_control.ControllerInactiveError):
        for current_left, _ in _fake_controller:
            await _fake_controller.update_bounds(current_left)

    assert _fake_controller.iterations == 3


@pytest.fixture
async def _fake_controller():
    class FakeBoundsControl(time_control.BoundsControl):
        def __init__(self):
            super().__init__(
                _fake_source(),
                datetime.datetime(2018, 10, 1, 12, 10),
                datetime.datetime(2018, 10, 1, 12, 30),
                datetime.timedelta(seconds=60),
                datetime.timedelta(seconds=60),
            )
            self.iterations = 0

        def __iter__(self):
            for _ in super().__iter__():
                self.iterations += 1
                yield _

    return FakeBoundsControl()


def _fake_source(iteration_type=consts.IterationType.MOVING_BOUNDARIES):
    class DummyMeta:
        time_chunk_size = datetime.timedelta(minutes=10)
        iteration_settings = iteration.make_settings(iteration_type)

    class DummySource:
        id = 'dummy_source'
        base_meta = DummyMeta

        async def get_next_stamp(self, current_ts):
            return current_ts

    return DummySource()


@pytest.mark.parametrize(
    'timestamp, ambiguous',
    [
        (datetime.datetime(2011, 3, 26, 1, 3), False),
        # +03 -> +04
        (datetime.datetime(2011, 3, 26, 20, 3), True),
        (datetime.datetime(2011, 3, 26, 21, 3), True),
        (datetime.datetime(2011, 3, 26, 22, 3), True),
        (datetime.datetime(2011, 3, 26, 23, 3), True),
        (datetime.datetime(2011, 3, 27, 0, 3), True),
        (datetime.datetime(2011, 3, 27, 1, 3), True),
        (datetime.datetime(2011, 3, 27, 8, 3), False),
        (datetime.datetime(2014, 10, 25, 10, 51, 33), False),
        # +04 -> +03
        (datetime.datetime(2014, 10, 25, 19, 51, 33), True),
        (datetime.datetime(2014, 10, 25, 20, 51, 33), True),
        (datetime.datetime(2014, 10, 25, 21, 51, 33), True),
        (datetime.datetime(2014, 10, 25, 22, 51, 33), True),
        (datetime.datetime(2014, 10, 26, 00, 51, 33), True),
        (datetime.datetime(2014, 10, 26, 2, 51, 33), True),
        (datetime.datetime(2016, 10, 25, 10, 51, 33), False),
        (12345, False),
    ],
)
def test_maybe_date_ambiguous(timestamp, ambiguous):
    assert (
        time_control._maybe_date_ambiguous(timestamp, time_control._MSK_TZ)
        == ambiguous
    )

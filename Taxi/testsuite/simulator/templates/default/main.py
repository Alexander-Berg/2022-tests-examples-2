# Entrypoint for simulator

import datetime
import random

import pytest

from simulator.core import initializers
from simulator.core import runner
from simulator.core import structures
from simulator.core.utils import current_time

START_TIME = '2021-02-01T12:00:00'


@pytest.mark.now(START_TIME, enabled=True)
# it is important to do several iterations, hint: keep it last parameter
@pytest.mark.parametrize(
    'iteration', [pytest.param(1, id='iter=1'), pytest.param(2, id='iter=2')],
)
@pytest.mark.simulator
async def test_simulate(
        dispatch_model,
        simulator_mocks,
        current_test_output_directory,
        iteration: int,
):
    """
        This test is generated, fill free to change it.
    """

    # make random not random, so each run will have the same result
    # it works only for python code and not for C++
    random.seed(42 * iteration)

    # initialize candidates online/offline events
    candidates = initializers.candidates.circle_n_generator.make_candidates(
        candidates_count=10,
        center=structures.Point(lat=55.5, lon=35.5),
        radius=100,
    )
    initializers.candidates.populate.allways_online(
        start=current_time.CurrentTime.get(), candidates=candidates,
    )

    # initialize new segment events
    segments = initializers.segments.circle_n_soon_generator.make_segments(
        segments_count=1,
        center=structures.Point(lat=55.5, lon=35.5),
        radius=100,
    )

    initializers.segments.populate.by_interval(
        start=current_time.CurrentTime.get(),
        end=current_time.CurrentTime.get() + datetime.timedelta(minutes=10),
        segments=segments,
    )

    # initialize dispatch
    initializers.dispatch.populate(
        start=current_time.CurrentTime.get(), planner_type='delivery',
    )

    # initialize simulation parameters (experiments3.0, configs, models etc.)
    # you can use fixtures from
    # services/united-dispatch/testsuite/tests_united_dispatch/plugins/experiments.py
    # (e.g. exp_delivery_gamble_settings) and pass any parameters

    # run simulation until finish
    runner_ = runner.Runner(
        folder_path=current_test_output_directory, use_cache=True,
    )

    await runner_.run()

    # gather statistics
    runner_.dump_raw_report()  # .output.log
    runner_.dump_statistics()  # .stats.log

    assert not runner_.is_failed

import uuid

import pytest

from simulator.core import initializers
from simulator.core import runner
from simulator.core import structures


@pytest.fixture(name='simulation_step')
async def _simulation_step(taxi_united_dispatch):
    async def wrapper(
            *,
            planner_type,
            segments,
            gamble_id=None,
            waybills=None,
            expected_status=200,
    ):
        if gamble_id is None:
            gamble_id = str(uuid.uuid4())
        if waybills is None:
            waybills = []
        response = await taxi_united_dispatch.post(
            '/simulation/step',
            json={
                'segments': segments,
                'waybills': waybills,
                'planner_type': planner_type,
                'gamble_id': gamble_id,
            },
        )
        assert response.status_code == expected_status
        return response.json()

    return wrapper


@pytest.fixture(name='build_input_segments')
def _build_input_segments(segment_builder):
    def wrapper(segments):
        return [{'info': segment_builder(seg)} for seg in segments]

    return wrapper


@pytest.fixture(name='create_simulator_candidates')
def _create_simulator_candidates(mocked_time):
    def wrapper(candidates_count=10):
        candidates = (
            initializers.candidates.circle_n_generator.make_candidates(
                candidates_count=candidates_count,
                center=structures.Point(lat=55.5, lon=35.5),
                radius=100,
            )
        )
        initializers.candidates.populate.allways_online(
            start=mocked_time.now(), candidates=candidates,
        )

    return wrapper


@pytest.fixture(name='launch_simulator_runner')
async def _launch_simulator_runner():
    async def wrapper():
        # run simulation until finish
        runner_ = runner.Runner()

        await runner_.run()

        assert not runner_.is_failed

        # gather statistics
        return runner_.iter_raw_report()

    return wrapper

import pathlib

import pytest

from simulator.core import config
from simulator.core import events
from simulator.core import modules
from simulator.core import queue
from simulator.core.utils import cleaner
from simulator.core.utils import current_time


@pytest.fixture(name='current_test_name')
def _current_test_name(request):
    """Return current test name"""
    return request.node.name


@pytest.fixture(name='current_test_directory', scope='module')
def _current_test_directory(request):
    """Return the directory of the currently running test script"""

    return request.fspath.join('..')


@pytest.fixture()
def current_test_output_directory(current_test_directory, current_test_name):
    """Return the directory of output for the currently running test"""

    path = pathlib.Path(f'{current_test_directory}/out/{current_test_name}')
    path.mkdir(parents=True, exist_ok=True)
    return str(path)


@pytest.fixture(autouse=True, name='clean_simulator')
async def _clean_simulator():
    cleaner.clear_all()


@pytest.fixture(name='dispatch_model')
async def _dispatch_model(
        united_dispatch_unit,
        mocked_time,
        clean_simulator,
        segment_builder,
        internal_waybill_builder,
        candidate_builder,
        state_initialized,
        exp_delivery_gamble_settings,
        exp_delivery_configs,
):
    await state_initialized()
    await exp_delivery_gamble_settings()
    await exp_delivery_configs()

    # reset singletones
    cleaner.clear_all()

    # config
    config.init()

    current_time.CurrentTime.set_fixtures(mocked_time=mocked_time)
    modules.DispatchModel.set_fixtures(
        united_dispatch=united_dispatch_unit,
        segment_builder=segment_builder,
        internal_waybill_builder=internal_waybill_builder,
        candidate_builder=candidate_builder,
    )

    queue.EventQueue.put(mocked_time.now(), events.statistics.pre_start())

    return modules.DispatchModel


@pytest.fixture(name='simulator_mocks')
async def _simulator_mocks(
        mock_simulator_driver_trackstory,
        mock_simulator_order_satisfy,
        mock_simulator_order_search,
        mock_simulator_scoring,
):
    pass

import datetime

import pytest

from abt import consts as app_consts
from test_abt import consts
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'get',
        '/v2/experiments',
        taxi_abt_web,
        default_params={'experiment_name': consts.DEFAULT_EXPERIMENT_NAME},
    )


@pytest.fixture(name='response_builder')
def _response_builder(abt):
    return abt.builders.get_response_builder('/v2/experiments')()


@pytest.mark.parametrize(
    'has_tracker_task, experiment_type',
    [
        pytest.param(True, 'experiment', id='has tracker task'),
        pytest.param(False, 'experiment', id='no tracker task'),
        pytest.param(True, 'config', id='config'),
        pytest.param(True, None, id='experiment as default type'),
    ],
)
async def test_success_response(
        abt,
        invoke_handler,
        response_builder,
        mockserver,
        load_json,
        has_tracker_task,
        experiment_type,
):
    await abt.state.add_experiment(
        experiment_type=experiment_type or 'experiment',
    )
    await abt.state.add_revision()

    def _get_exp_resp():
        resp = load_json('taxi_exp_experiments_resp.json')
        if not has_tracker_task:
            resp['st_tickets'] = []
        return mockserver.make_response(json=resp)

    @mockserver.json_handler('/taxi-exp/v1/configs/')
    def _v1_configs(request):
        return _get_exp_resp()

    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _v1_experiments(request):
        return _get_exp_resp()

    params = {'experiment_name': consts.DEFAULT_EXPERIMENT_NAME}

    if experiment_type is not None:
        params['type'] = experiment_type

    got = await invoke_handler(params=params)

    expected = response_builder.add_revision()

    if not has_tracker_task:
        expected.set_tracker_task(None)

    assert got == expected.build()


async def test_experiment_not_found(invoke_handler):
    got = await invoke_handler(
        params={'experiment_name': 'absent_experiment'}, expected_code=404,
    )

    assert got['code'] == app_consts.CODE_404


async def test_revisions_order(
        abt, invoke_handler, response_builder, mockserver, load_json,
):
    await abt.state.add_experiment()

    time = consts.DEFAULT_REVISION_STARTED_AT
    time_later = time + datetime.timedelta(days=1)

    await abt.state.add_revision(revision_id=1, started_at=time)
    await abt.state.add_revision(revision_id=2, started_at=time_later)

    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _v1_experiments(request):
        return mockserver.make_response(
            json=load_json('taxi_exp_experiments_resp.json'),
        )

    got = await invoke_handler()

    response_builder.add_revision(revision_id=2, started_at=time_later)
    response_builder.add_revision(revision_id=1, started_at=time)

    assert got == response_builder.build()


async def test_taxi_exp_404(abt, mockserver, invoke_handler):
    await abt.state.add_experiment()
    await abt.state.add_revision()

    @mockserver.json_handler('/taxi-exp/v1/experiments/')
    def _v1_experiments(request):
        return mockserver.make_response(status=404)

    got = await invoke_handler(expected_code=404)

    assert got['code'] == app_consts.CODE_404

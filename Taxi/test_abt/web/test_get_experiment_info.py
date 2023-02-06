import datetime

import pytest

from test_abt import consts
from test_abt.helpers import web as web_helpers


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web):
    return web_helpers.create_invoke(
        'get',
        '/v1/experiments',
        taxi_abt_web,
        default_params={'experiment_name': consts.DEFAULT_EXPERIMENT_NAME},
    )


@pytest.fixture(name='response_builder')
def _response_builder(abt):
    return abt.builders.get_response_builder('/v1/experiments')()


async def test_get_experiment_info(abt, invoke_handler, response_builder):
    await abt.state.add_experiment()
    await abt.state.add_revision()
    await abt.state.add_revision_group()

    got = await invoke_handler()

    expected_response = response_builder.add_revision().build()

    assert got == expected_response


async def test_experiment_not_found(invoke_handler):
    got = await invoke_handler(
        params={'experiment_name': 'absent_experiment'}, expected_code=404,
    )

    assert got == {
        'code': 'not_found',
        'message': 'Experiment absent_experiment not found',
    }


@pytest.mark.config(ABT_REVISION_CONTROL_GROUP_REGEX_LIST=[r'Some\s+title'])
async def test_control_group_detection_by_config(
        abt, invoke_handler, response_builder,
):
    await abt.state.add_experiment()
    await abt.state.add_revision()
    await abt.state.add_revision_group()
    await abt.state.add_revision_group(group_id=2, title='some title')

    await abt.state.add_revision(revision_id=2)
    await abt.state.add_revision_group(revision_id=2)
    await abt.state.add_revision_group(
        revision_id=2, group_id=2, title='another title',
    )
    await abt.state.add_revision_group(
        revision_id=2, group_id=3, title='some title',
    )
    await abt.state.add_revision_group(
        revision_id=2, group_id=4, title='some title 2',
    )

    expected_response = (
        response_builder.add_revision()
        .add_revision_group(
            group_id=2, title='some title', is_control=True, is_selected=True,
        )
        .add_revision(revision_id=2)
        .add_revision_group(
            revision_id=2,
            group_id=2,
            title='another title',
            is_control=False,
            is_selected=False,
        )
        .add_revision_group(
            revision_id=2,
            group_id=3,
            title='some title',
            is_control=True,
            is_selected=True,
        )
        .add_revision_group(
            revision_id=2,
            group_id=4,
            title='some title 2',
            is_control=False,
            is_selected=False,
        )
        .build()
    )

    got = await invoke_handler()

    assert got == expected_response


async def test_revisions_order(abt, invoke_handler, response_builder):
    await abt.state.add_experiment()

    time = consts.DEFAULT_REVISION_STARTED_AT
    time_later = time + datetime.timedelta(days=1)

    await abt.state.add_revision(revision_id=1, started_at=time)
    await abt.state.add_revision(revision_id=2, started_at=time_later)

    await abt.state.add_revision_group(revision_id=1)
    await abt.state.add_revision_group(revision_id=2)

    got = await invoke_handler()

    response_builder.add_revision(revision_id=2, started_at=time_later)
    response_builder.add_revision(revision_id=1, started_at=time)

    expected_response = response_builder.build()

    assert got == expected_response

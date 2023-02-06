import pathlib
import shutil
from unittest import mock

import pytest

from taxi.stq import async_worker_ng

from abt.stq import update_docs


@pytest.fixture(name='prepare_state')
async def prepare_state_fixture(abt):
    async def _inner(precomputes_table=None):
        metrics_group_1 = await abt.state.add_metrics_group()

        metrics_group_2 = await abt.state.add_metrics_group(
            config=abt.builders.get_mg_config_builder()
            .add_value_metric()
            .add_precomputes(
                facets=abt.builders.get_facets_builder()
                .add_custom_facet('ios', ['ios'])
                .add_custom_facet('android', ['android'])
                .build(),
            )
            .build(),
        )

        if precomputes_table is None:
            precomputes_table = await abt.state.add_precomputes_table()

        await abt.state.bind_mg_with_pt(
            metrics_group_1['id'], precomputes_table['id'],
        )
        await abt.state.bind_mg_with_pt(
            metrics_group_2['id'], precomputes_table['id'],
        )

        return [metrics_group_1, metrics_group_2], precomputes_table

    return _inner


async def test_daas_called(stq_context, prepare_state, mockserver):
    @mockserver.handler(f'/yandex-doc/v1/projects/0/async_deploy')
    def async_deploy(request):
        assert request.method == 'POST'
        assert request.headers['Authorization'] == 'OAuth oauth-token'
        assert request.content_type == 'multipart/form-data'
        return mockserver.make_response('', status=200)

    await prepare_state()
    await update_docs.task(stq_context, _build_task_info())
    assert async_deploy.times_called == 1


async def test_structure(stq_context, prepare_state, mockserver):
    @mockserver.handler(f'/yandex-doc/v1/projects/0/async_deploy')
    def _patched(request):
        return mockserver.make_response('', status=200)

    metrics_groups, _ = await prepare_state()

    task_info = _build_task_info()
    work_dir = pathlib.Path(f'/tmp/abt_docs_{task_info.id}')
    if work_dir.exists():
        shutil.rmtree(work_dir)

    # mock rmtree function so work_dir still will be exist after stq completes
    # to assert its contents
    with mock.patch('shutil.rmtree'):
        await update_docs.task(stq_context, task_info)

    assert work_dir.exists()
    assert (work_dir / 'index.rst').exists()
    assert (work_dir / 'metrics_groups').exists()
    for metric_group in metrics_groups:
        assert (
            work_dir / 'metrics_groups' / f'{metric_group["id"]}.rst'
        ).exists()
    assert (work_dir / 'docs').exists()
    assert (work_dir / 'docs.tar.gz').exists()

    shutil.rmtree(work_dir)


@pytest.mark.config(
    ABT_FACETS_V2={'ios': {'description': 'ios facet', 'title_key': 'test'}},
)
async def test_docs_generator(stq_context, prepare_state, mockserver, load):
    @mockserver.handler(f'/yandex-doc/v1/projects/0/async_deploy')
    def _patched(request):
        return mockserver.make_response('', status=200)

    metrics_groups, _ = await prepare_state()

    task_info = _build_task_info()
    work_dir = pathlib.Path(f'/tmp/abt_docs_{task_info.id}')
    if work_dir.exists():
        shutil.rmtree(work_dir)

    with mock.patch('shutil.rmtree'):
        await update_docs.task(stq_context, task_info)

    files_to_check = ['index.rst']
    for metrics_group in metrics_groups:
        files_to_check.append(f'metrics_groups/{metrics_group["id"]}.rst')

    for filename in files_to_check:
        expected_content = load(filename.replace('/', '_'))
        with open(work_dir / filename, 'r') as generated_file:
            assert generated_file.read() == expected_content

    shutil.rmtree(work_dir)


def _build_task_info():
    return async_worker_ng.TaskInfo(
        id=1, exec_tries=1, reschedule_counter=1, queue='',
    )

import dataclasses
import datetime
import typing as tp

import pytest

from taxi.stq import async_worker_ng
from taxi.util import dates as dates_utils

from abt import models
from abt.stq import abt_index_precomputes
from test_abt import consts
from test_abt import utils


CURRENT_TIME = '2020-01-01T23:55:00+0000'


def days(num: int) -> datetime.timedelta:
    return datetime.timedelta(days=num)


def build_task_info(table_id: int):
    return async_worker_ng.TaskInfo(
        id=table_id,
        exec_tries=1,
        reschedule_counter=1,
        queue='abt_index_precomputes',
    )


@dataclasses.dataclass
class Case:
    initial_revisions: tp.List[models.Revision]
    analyze_precomputes_table_response: tp.List[dict]
    lookup_rows_response: tp.Optional[dict]
    revisions_response: tp.Optional[dict]
    expected_experiments: tp.List[models.Experiment]
    expected_revisions: tp.List[models.Revision]
    expected_facets: tp.List[dict]


@pytest.mark.now(CURRENT_TIME)
@pytest.mark.parametrize(
    'testcase',
    [
        pytest.param(
            Case(
                initial_revisions=[
                    models.Revision(
                        id=100,
                        business_revision_id=1,
                        business_min_version_id=100,
                        business_max_version_id=120,
                        experiment_id=1,
                        started_at=consts.DEFAULT_REVISION_STARTED_AT,
                        ended_at=None,
                        data_available_days=['a', 'b', 'c'],
                    ),
                ],
                analyze_precomputes_table_response=[
                    {
                        'revision_id': 136,
                        'data_available_days': ['b', 'c', 'd'],
                        'facets': ['kitty', 'android'],
                    },
                    {
                        'revision_id': 150,
                        'data_available_days': ['c', 'd'],
                        'facets': ['goodboy'],
                    },
                ],
                lookup_rows_response={
                    'items': [
                        {'name': 'exp_1', 'is_config': False, 'rev': 136},
                        {'name': 'exp_2', 'is_config': False, 'rev': 150},
                    ],
                },
                revisions_response={
                    'exp_1': {
                        'revisions': [
                            {
                                'revision': 135,
                                'biz_revision': 2,
                                'updated': '2020-11-11T10:10:10.000+03:00',
                            },
                            {
                                'revision': 136,
                                'biz_revision': 2,
                                'updated': '2020-11-12T10:10:10.000+03:00',
                            },
                        ],
                        'stop': 136,
                    },
                    'exp_2': {
                        'revisions': [
                            {
                                'revision': 150,
                                'biz_revision': 1,
                                'updated': '2021-11-11T10:10:10.000+03:00',
                            },
                        ],
                        'stop': 150,
                    },
                },
                expected_experiments=[
                    models.Experiment(
                        id=1,
                        name='exp_1',
                        type=models.ExperimentType.Experiment,
                        description=consts.DEFAULT_EXPERIMENT_DESCRIPTION,
                    ),
                    models.Experiment(
                        id=2,
                        name='exp_2',
                        type=models.ExperimentType.Experiment,
                        description=None,
                    ),
                ],
                expected_revisions=[
                    models.Revision(
                        id=100,
                        business_revision_id=1,
                        business_min_version_id=100,
                        business_max_version_id=120,
                        experiment_id=1,
                        started_at=consts.DEFAULT_REVISION_STARTED_AT,
                        ended_at=dates_utils.parse_timestring_aware(
                            '2020-11-11T10:10:10.000+03:00',
                        ),
                        data_available_days=['a', 'b', 'c'],
                    ),
                    models.Revision(
                        id=136,
                        business_revision_id=2,
                        business_min_version_id=135,
                        business_max_version_id=136,
                        experiment_id=1,
                        started_at=dates_utils.parse_timestring_aware(
                            '2020-11-11T10:10:10.000+03:00',
                        ),
                        ended_at=None,
                        data_available_days=['b', 'c', 'd'],
                    ),
                    models.Revision(
                        id=150,
                        business_revision_id=1,
                        business_min_version_id=150,
                        business_max_version_id=150,
                        experiment_id=2,
                        started_at=dates_utils.parse_timestring_aware(
                            '2021-11-11T10:10:10.000+03:00',
                        ),
                        ended_at=None,
                        data_available_days=['c', 'd'],
                    ),
                ],
                expected_facets=[
                    {'revision_id': 136, 'facet': 'android'},
                    {'revision_id': 136, 'facet': 'kitty'},
                    {'revision_id': 150, 'facet': 'goodboy'},
                ],
            ),
            id='new revision created and old updated',
        ),
        pytest.param(
            Case(
                initial_revisions=[
                    models.Revision(
                        id=100,
                        business_revision_id=1,
                        business_min_version_id=100,
                        business_max_version_id=120,
                        experiment_id=1,
                        started_at=consts.DEFAULT_REVISION_STARTED_AT,
                        ended_at=None,
                        data_available_days=['a', 'b', 'c'],
                    ),
                ],
                analyze_precomputes_table_response=[],
                lookup_rows_response=None,
                revisions_response=None,
                expected_experiments=[
                    models.Experiment(
                        id=1,
                        name='exp_1',
                        type=models.ExperimentType.Experiment,
                        description=consts.DEFAULT_EXPERIMENT_DESCRIPTION,
                    ),
                ],
                expected_revisions=[],
                expected_facets=[],
            ),
            id='remove the only one revision',
        ),
        pytest.param(
            Case(
                initial_revisions=[],
                analyze_precomputes_table_response=[
                    {
                        'revision_id': 10,
                        'data_available_days': ['a'],
                        'facets': [],
                    },
                    {
                        'revision_id': 11,
                        'data_available_days': ['b'],
                        'facets': [],
                    },
                ],
                lookup_rows_response={
                    'items': [
                        {'name': 'exp_1', 'is_config': False, 'rev': 10},
                        {'name': 'exp_1', 'is_config': False, 'rev': 11},
                    ],
                },
                revisions_response={
                    'exp_1': {
                        'revisions': [
                            {
                                'revision': 10,
                                'biz_revision': 1,
                                'updated': '2020-11-11T10:10:10.000+03:00',
                            },
                            {
                                'revision': 11,
                                'biz_revision': 1,
                                'updated': '2020-11-12T10:10:10.000+03:00',
                            },
                        ],
                        'stop': 11,
                    },
                },
                expected_experiments=[
                    models.Experiment(
                        id=1,
                        name='exp_1',
                        type=models.ExperimentType.Experiment,
                        description=None,
                    ),
                ],
                expected_revisions=[
                    models.Revision(
                        id=11,
                        business_revision_id=1,
                        business_min_version_id=10,
                        business_max_version_id=11,
                        experiment_id=1,
                        started_at=dates_utils.parse_timestring_aware(
                            '2020-11-11T10:10:10.000+03:00',
                        ),
                        ended_at=None,
                        data_available_days=['b'],
                    ),
                ],
                expected_facets=[],
            ),
            id=(
                'precomputes table contains several revisions '
                'for one biz_revision'
            ),
        ),
        pytest.param(
            Case(
                initial_revisions=[
                    models.Revision(
                        id=100,
                        business_revision_id=1,
                        business_min_version_id=100,
                        business_max_version_id=110,
                        experiment_id=1,
                        started_at=consts.DEFAULT_REVISION_STARTED_AT,
                        ended_at=None,
                        data_available_days=['a', 'b', 'c'],
                    ),
                ],
                analyze_precomputes_table_response=[
                    {
                        'revision_id': 100,
                        'data_available_days': ['a'],
                        'facets': [],
                    },
                    {
                        'revision_id': 100500,
                        'data_available_days': ['z'],
                        'facets': [],
                    },
                ],
                lookup_rows_response={
                    'items': [
                        {'name': 'exp_1', 'is_config': False, 'rev': 100},
                    ],
                },
                revisions_response={
                    'exp_1': {
                        'revisions': [
                            {
                                'revision': 120,
                                'biz_revision': 1,
                                'updated': '2020-11-11T10:10:10.000+03:00',
                            },
                        ],
                        'stop': 120,
                    },
                },
                expected_experiments=[
                    models.Experiment(
                        id=1,
                        name='exp_1',
                        type=models.ExperimentType.Experiment,
                        description=consts.DEFAULT_EXPERIMENT_DESCRIPTION,
                    ),
                ],
                expected_revisions=[
                    models.Revision(
                        id=100,
                        business_revision_id=1,
                        business_min_version_id=100,
                        business_max_version_id=120,
                        experiment_id=1,
                        started_at=consts.DEFAULT_REVISION_STARTED_AT,
                        ended_at=None,
                        data_available_days=['a', 'b', 'c'],
                    ),
                ],
                expected_facets=[],
            ),
            id='archive-api has no info about revision',
        ),
        pytest.param(
            Case(
                initial_revisions=[],
                analyze_precomputes_table_response=[
                    {
                        'revision_id': 100,
                        'data_available_days': ['a'],
                        'facets': [],
                    },
                ],
                lookup_rows_response={
                    'items': [
                        {'name': 'exp_1', 'is_config': True, 'rev': 100},
                    ],
                },
                revisions_response={
                    'exp_1': {
                        'revisions': [
                            {
                                'revision': 100,
                                'biz_revision': 1,
                                'updated': '2020-11-11T10:10:10.000+03:00',
                            },
                        ],
                        'stop': 100,
                    },
                },
                expected_experiments=[
                    models.Experiment(
                        id=1,
                        name='exp_1',
                        type=models.ExperimentType.Config,
                        description=None,
                    ),
                ],
                expected_revisions=[
                    models.Revision(
                        id=100,
                        business_revision_id=1,
                        business_min_version_id=100,
                        business_max_version_id=100,
                        experiment_id=1,
                        started_at=dates_utils.parse_timestring_aware(
                            '2020-11-11T10:10:10.000+03:00',
                        ),
                        ended_at=None,
                        data_available_days=['a'],
                    ),
                ],
                expected_facets=[],
            ),
            id='create config',
        ),
    ],
)
async def test_index_precomputes(
        abt,
        stq_context,
        yt_apply,
        mocked_time,
        mocked_stq_context,
        mockserver,
        testcase,
):
    metrics_group = await abt.state.add_metrics_group()
    precomputes_table = await abt.state.add_precomputes_table()
    await abt.state.bind_mg_with_pt(
        metrics_group['id'], precomputes_table['id'],
    )

    _experiments = set()

    for revision in testcase.initial_revisions:
        if revision.experiment_id not in _experiments:
            await abt.state.add_experiment(
                name=f'exp_{revision.experiment_id}',
            )
            _experiments.add(revision.experiment_id)
        await abt.state.add_revision(
            revision_id=revision.id,
            started_at=revision.started_at,
            ended_at=revision.ended_at,
            data_available_days=revision.data_available_days,
            business_revision_id=revision.business_revision_id,
            business_min_version_id=revision.business_min_version_id,
            business_max_version_id=revision.business_max_version_id,
        )

    mocked_stq_context.chyt_clients.set_mock_response(
        'analyze_precomputes_table',
        testcase.analyze_precomputes_table_response,
    )

    @mockserver.json_handler('/archive-api/v1/yt/lookup_rows')
    def _lookup_rows(request):
        return mockserver.make_response(json=testcase.lookup_rows_response)

    def _get_revisions(request):
        exp_info = testcase.revisions_response[request.args['name']]
        return mockserver.make_response(
            json={
                'revisions': (
                    exp_info['revisions']
                    if int(request.args['newer_than']) < exp_info['stop']
                    else []
                ),
            },
        )

    @mockserver.json_handler('/taxi-exp/v1/experiments/revisions/')
    def _experiments_revisions(request):
        return _get_revisions(request)

    @mockserver.json_handler('/taxi-exp/v1/configs/revisions/')
    def _configs_revisions(request):
        return _get_revisions(request)

    await abt_index_precomputes.task(
        mocked_stq_context,
        build_task_info(precomputes_table['id']),
        consts.DEFAULT_YT_CLUSTER,
        consts.DEFAULT_YT_PATH,
    )

    assert len(mocked_stq_context.chyt_clients.calls) == 1
    assert _lookup_rows.times_called == (
        1 if testcase.lookup_rows_response else 0
    )

    assert (
        (_experiments_revisions.times_called + _configs_revisions.times_called)
        == (
            len(testcase.revisions_response) * 2
            if testcase.revisions_response
            else 0
        )
    )

    assert testcase.expected_experiments == [
        models.Experiment.from_record(exp)
        for exp in await abt.pg.experiments.all()
    ]
    assert testcase.expected_revisions == [
        models.Revision.from_record(rev)
        for rev in await abt.pg.revisions.all()
    ]
    assert testcase.expected_facets == [
        utils.fields(facet, ['revision_id', 'facet'])
        for facet in await abt.pg.facets.all(order_by='(revision_id, facet)')
    ]

    indexed_at = (
        await abt.pg.precomputes_tables.by_id(precomputes_table['id'])
    )['indexed_at']

    assert indexed_at is not None


@pytest.mark.parametrize('pass_metrics_group_id', [True, False])
async def test_sync_local_table(
        abt, mocked_stq_context, yt_apply, pass_metrics_group_id,
):
    table_before = await abt.state.add_precomputes_table(
        facets={
            'sys': {
                'date': {'column': 'notdate'},
                'group': {'column': 'notgroup'},
                'bucket': {'column': 'notbucket'},
                'revision': {'column': 'notrevision'},
            },
        },
        attributes={
            'is_sorted': False,
            'sorted_by': ['revision'],
            'is_dynamic': False,
        },
    )

    metrics_group = await abt.state.add_metrics_group()

    await abt.state.bind_mg_with_pt(metrics_group['id'], table_before['id'])

    mocked_stq_context.chyt_clients.set_mock_response(
        'analyze_precomputes_table', [],
    )

    args = (
        mocked_stq_context,
        build_task_info(table_before['id']),
        consts.DEFAULT_YT_CLUSTER,
        consts.DEFAULT_YT_PATH,
    )
    kwargs = {}

    if pass_metrics_group_id:
        kwargs['metrics_group_id'] = metrics_group['id']

    await abt_index_precomputes.task(*args, **kwargs)

    table_after = await abt.pg.precomputes_tables.by_id(table_before['id'])

    assert table_before['schema'] != table_after['schema']
    assert table_before['attributes'] != table_after['attributes']
    assert (
        table_before['facets'] != table_after['facets']
    ) == pass_metrics_group_id

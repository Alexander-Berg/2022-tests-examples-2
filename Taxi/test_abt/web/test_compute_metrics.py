# pylint: disable=C0302

import copy
import dataclasses
import typing as tp

import pytest

from abt import consts as app_consts
from abt import models
from abt.api import compute_metrics
from abt.generated.service.swagger.models import api as api_models
from abt.utils import sphinx
from test_abt import consts
from test_abt import utils
from test_abt.helpers import web as web_helpers


DEFAULT_REQUEST = {
    'experiment_name': consts.DEFAULT_EXPERIMENT_NAME,
    'experiment_groups': {'control': 1, 'test': [2]},
    'experiment_revision': consts.DEFAULT_REVISION_ID,
    'revision_days': consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
}

CONTROL_MEASURES = range(0, 10)

CONTROL_MEASURES_SUM = '45,0'

TEST_MEASURES = range(10, 20)

TEST_FACET = 'littlepony'

TVM_RULES = pytest.mark.config(TVM_RULES=[{'src': 'abt', 'dst': 'taxi_exp'}])


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web, mocked_web_request, mockserver, load_json):
    async def _inner(
            body=utils.Sentinel(),
            *,
            expected_code=200,
            mocked_context=None,
            taxi_exp_code=200,
            taxi_exp_response=None,
    ):
        @mockserver.json_handler('/taxi-exp/v1/history/')
        def _v1_history(request):
            return mockserver.make_response(
                json=(
                    taxi_exp_response
                    or load_json('taxi_exp_history_resp.json')
                ),
                status=taxi_exp_code,
            )

        if mocked_context is None:
            return await web_helpers.create_invoke(
                'post',
                '/v1/metrics',
                taxi_abt_web,
                default_body=DEFAULT_REQUEST,
            )(body=body, expected_code=expected_code)

        async def _mock_req_func(endpoint, **kwargs):
            return await compute_metrics.handle(
                mocked_web_request(
                    api_models.MetricsRequest.deserialize(kwargs['json']),
                ),
                mocked_context,
            )

        async def _mock_resp_parser(response):
            return response.data.serialize()

        return await web_helpers.create_invoke(
            'post',
            '/v1/metrics',
            taxi_abt_web,
            req_func=_mock_req_func,
            resp_parser=_mock_resp_parser,
            default_body=DEFAULT_REQUEST,
        )(body=body, expected_code=expected_code)

    return _inner


@pytest.fixture(name='get_response_builder')
def _response_builder(abt):
    def _inner(control_group, test_groups):
        return abt.builders.get_response_builder('/v1/metrics')(
            control_group, test_groups,
        )

    return _inner


@dataclasses.dataclass(frozen=True)
class State:
    metrics_config: dict
    collapsed_metrics_group: models.MetricsGroup
    expanded_metrics_group: models.MetricsGroup
    hidden_metrics_group: models.MetricsGroup
    precomputes_table: models.PrecomputesTable
    control_group: models.RevisionsGroup
    test_group: models.RevisionsGroup
    second_test_group: models.RevisionsGroup
    control_measures: tp.List[dict]
    test_measures: tp.List[dict]
    second_test_measures: tp.List[dict]
    revision: models.Revision


@pytest.fixture(name='prepare_state')
async def prepare_state_fixture(abt):
    async def _inner(
            metric_greater_is_better=None,
            collapsed_position=consts.DEFAULT_METRICS_GROUP_POSITION,
            expanded_position=consts.DEFAULT_METRICS_GROUP_POSITION,
            hidden_position=consts.DEFAULT_METRICS_GROUP_POSITION,
            add_collapsed=True,
            add_expanded=True,
            add_hidden=True,
            table_schema=None,
            metrics_config=None,
    ):
        metrics_config = (
            metrics_config
            if metrics_config
            else abt.builders.get_mg_config_builder()
            .add_value_metric(greater_is_better=metric_greater_is_better)
            .add_precomputes()
            .build()
        )

        table_schema = (
            table_schema
            if table_schema
            else abt.builders.get_pt_schema_builder()
            .add_column(consts.DEFAULT_VALUE_COLUMN)
            .build()
        )

        precomputes_table = models.PrecomputesTable.from_record(
            await abt.state.add_precomputes_table(schema=table_schema),
        )

        if add_expanded:
            expanded_metrics_group = models.MetricsGroup.from_record(
                await abt.state.add_metrics_group(
                    is_collapsed=False,
                    enabled=True,
                    config=metrics_config,
                    position=expanded_position,
                ),
            )
            await abt.state.bind_mg_with_pt(
                expanded_metrics_group.id, precomputes_table.id,
            )

        if add_collapsed:
            collapsed_metrics_group = models.MetricsGroup.from_record(
                await abt.state.add_metrics_group(
                    is_collapsed=True,
                    enabled=True,
                    config=metrics_config,
                    position=collapsed_position,
                ),
            )
            await abt.state.bind_mg_with_pt(
                collapsed_metrics_group.id, precomputes_table.id,
            )

        if add_hidden:
            hidden_metrics_group = models.MetricsGroup.from_record(
                await abt.state.add_metrics_group(
                    is_collapsed=True,
                    enabled=False,
                    config=metrics_config,
                    position=hidden_position,
                ),
            )
            await abt.state.bind_mg_with_pt(
                hidden_metrics_group.id, precomputes_table.id,
            )

        experiment = models.Experiment.from_record(
            await abt.state.add_experiment(),
        )

        await abt.state.bind_pt_with_experiment(
            precomputes_table.id, experiment.id,
        )

        revision = models.Revision.from_record(await abt.state.add_revision())

        control_group = models.RevisionsGroup(
            revision_id=-1, group_id=1, title='control revision group',
        )
        test_group = models.RevisionsGroup(
            revision_id=-1, group_id=2, title='first test revision group',
        )
        second_test_group = models.RevisionsGroup(
            revision_id=-1, group_id=3, title='second test revision group',
        )

        control_measures = (
            abt.builders.get_measures_builder(
                revision.id, control_group.group_id, buckets_count=10,
            )
            .add_column(consts.DEFAULT_VALUE_COLUMN, CONTROL_MEASURES)
            .build()
        )

        test_measures = (
            abt.builders.get_measures_builder(
                revision.id, test_group.group_id, buckets_count=10,
            )
            .add_column(consts.DEFAULT_VALUE_COLUMN, TEST_MEASURES)
            .build()
        )

        second_test_measures = (
            abt.builders.get_measures_builder(
                revision.id, second_test_group.group_id, buckets_count=10,
            )
            .add_column(consts.DEFAULT_VALUE_COLUMN, TEST_MEASURES)
            .build()
        )

        await abt.state.add_facets(
            TEST_FACET, precomputes_table.id, revision.id,
        )

        return State(
            metrics_config=metrics_config,
            collapsed_metrics_group=collapsed_metrics_group
            if add_collapsed
            else None,
            expanded_metrics_group=expanded_metrics_group
            if add_expanded
            else None,
            hidden_metrics_group=hidden_metrics_group if add_hidden else None,
            precomputes_table=precomputes_table,
            control_group=control_group,
            test_group=test_group,
            second_test_group=second_test_group,
            control_measures=control_measures,
            test_measures=test_measures,
            second_test_measures=second_test_measures,
            revision=revision,
        )

    return _inner


def prepare_metric(builder, **kwargs):
    default_kwargs = {
        'value': '145,0',
        'abs_diff': '+100,0',
        'rel_diff': '+222,22%',
        'mannwhitneyu': '0,0002',
        'shapiro': '0,892',
        'ttest': '0,0',
    }

    return builder(**{**default_kwargs, **kwargs})


@pytest.mark.parametrize(
    'data,expected_code',
    [
        pytest.param(
            {**DEFAULT_REQUEST, **{'experiment_revision': 100500}},
            404,
            id='revision not found',
        ),
        pytest.param(
            {**DEFAULT_REQUEST, **{'revision_days': ['1990-04-15']}},
            404,
            id='incorrect revision days passed',
        ),
        pytest.param(
            {
                **DEFAULT_REQUEST,
                **{'experiment_groups': {'control': 100500, 'test': [100501]}},
            },
            404,
            id='incorrect experiment groups',
        ),
        pytest.param(
            {**DEFAULT_REQUEST, **{'revision_days': []}},
            400,
            id='Empty revisions days list',
        ),
    ],
)
async def test_validation_errors(abt, invoke_handler, data, expected_code):
    await abt.state.add_experiment()
    await abt.state.add_revision()
    await abt.state.add_revision_group(group_id=1)
    await abt.state.add_revision_group(group_id=2)

    await invoke_handler(data, expected_code=expected_code)


async def test_no_metrics_groups_passed(
        abt,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        get_response_builder,
):
    state = await prepare_state()

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    response_builder = get_response_builder(
        state.control_group, [state.test_group],
    )

    got = await invoke_handler(mocked_context=mocked_web_context)

    response_builder.add_metrics_group(
        metrics_group=state.expanded_metrics_group,
        metrics=[
            response_builder.create_metric(
                control_value=CONTROL_MEASURES_SUM,
                test=[
                    prepare_metric(response_builder.create_test_metric_values),
                ],
            ),
        ],
    )
    response_builder.add_metrics_group(
        metrics_group=state.collapsed_metrics_group,
        metrics=[
            response_builder.create_metric(
                control_value=CONTROL_MEASURES_SUM,
                test=[
                    prepare_metric(response_builder.create_test_metric_values),
                ],
            ),
        ],
    )
    response_builder.add_metrics_group(
        metrics_group=state.hidden_metrics_group,
    )

    assert got == response_builder.build()


async def test_metrics_groups_passed(
        abt,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        get_response_builder,
):
    state = await prepare_state()

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    got = await invoke_handler(
        {
            **DEFAULT_REQUEST,
            'metrics_groups': [state.collapsed_metrics_group.id],
        },
        mocked_context=mocked_web_context,
    )

    response_builder = get_response_builder(
        state.control_group, [state.test_group],
    )

    expected_response = response_builder.add_metrics_group(
        metrics_group=state.collapsed_metrics_group,
        metrics=[
            response_builder.create_metric(
                control_value=CONTROL_MEASURES_SUM,
                test=[
                    prepare_metric(response_builder.create_test_metric_values),
                ],
            ),
        ],
    ).build()

    assert got == expected_response


@pytest.mark.config(
    ABT_RESPONSES_CACHE={
        'enabled': True,
        'handles_settings': [{'uri': '/v1/metrics', 'item_life_time': 604800}],
    },
)
async def test_using_cache_simple(
        abt,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        get_response_builder,
):
    state = await prepare_state()

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    for _ in range(2):
        got = await invoke_handler(
            {
                **DEFAULT_REQUEST,
                'metrics_groups': [state.collapsed_metrics_group.id],
            },
            mocked_context=mocked_web_context,
        )

        response_builder = get_response_builder(
            state.control_group, [state.test_group],
        )

        expected_response = response_builder.add_metrics_group(
            metrics_group=state.collapsed_metrics_group,
            metrics=[
                response_builder.create_metric(
                    control_value=CONTROL_MEASURES_SUM,
                    test=[
                        prepare_metric(
                            response_builder.create_test_metric_values,
                        ),
                    ],
                ),
            ],
        ).build()

        assert got == expected_response

    assert len(mocked_web_context.chyt_clients.calls) == 1


@pytest.mark.config(
    ABT_RESPONSES_CACHE={
        'enabled': True,
        'handles_settings': [{'uri': '/v1/metrics', 'item_life_time': 604800}],
    },
)
async def test_caching_all_revision_groups(
        abt,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        get_response_builder,
):
    state = await prepare_state()
    await abt.state.add_revision_group(group_id=1)
    await abt.state.add_revision_group(group_id=2)
    await abt.state.add_revision_group(group_id=3)

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes',
        state.control_measures
        + state.test_measures
        + state.second_test_measures,
    )

    for test_group in [state.test_group, state.second_test_group]:
        request = copy.deepcopy(DEFAULT_REQUEST)
        request['experiment_groups']['test'] = [test_group.group_id]

        got = await invoke_handler(
            {**request, 'metrics_groups': [state.collapsed_metrics_group.id]},
            mocked_context=mocked_web_context,
        )

        response_builder = get_response_builder(
            state.control_group, [test_group],
        )

        expected_response = response_builder.add_metrics_group(
            metrics_group=state.collapsed_metrics_group,
            metrics=[
                response_builder.create_metric(
                    control_value=CONTROL_MEASURES_SUM,
                    test=[
                        prepare_metric(
                            response_builder.create_test_metric_values,
                        ),
                    ],
                ),
            ],
        ).build()

        assert (
            got == expected_response
        ), f'Incorrect response for {test_group.group_id}'

    assert len(mocked_web_context.chyt_clients.calls) == 1


@pytest.mark.config(
    ABT_RESPONSES_CACHE={
        'enabled': True,
        'handles_settings': [{'uri': '/v1/metrics', 'item_life_time': 604800}],
    },
)
async def test_recache_if_metrics_group_is_obsolete(
        abt,
        pgsql,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        get_response_builder,
):
    state = await prepare_state()
    await abt.state.add_revision_group(group_id=1)
    await abt.state.add_revision_group(group_id=2)
    await abt.state.add_revision_group(group_id=3)

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    def _update_mg_version(mg_version):
        cursor = pgsql['abt'].cursor()
        cursor.execute(
            f'UPDATE abt.metrics_groups ' f'SET version={mg_version}',
        )
        cursor.close()

    async def _invoke_cache(mg_version):
        got = await invoke_handler(
            {
                **DEFAULT_REQUEST,
                'metrics_groups': [state.collapsed_metrics_group.id],
            },
            mocked_context=mocked_web_context,
        )

        response_builder = get_response_builder(
            state.control_group, [state.test_group],
        )

        overwritten_collapsed_mg = models.MetricsGroup(
            id=state.collapsed_metrics_group.id,
            title=state.collapsed_metrics_group.title,
            description=state.collapsed_metrics_group.description,
            owners=state.collapsed_metrics_group.owners,
            scopes=state.collapsed_metrics_group.scopes,
            is_collapsed=state.collapsed_metrics_group.is_collapsed,
            enabled=state.collapsed_metrics_group.enabled,
            updated_at=state.collapsed_metrics_group.updated_at,
            created_at=state.collapsed_metrics_group.created_at,
            version=mg_version,
            position=state.collapsed_metrics_group.position,
            config_source=state.collapsed_metrics_group.config_source,
        )
        expected_response = response_builder.add_metrics_group(
            metrics_group=overwritten_collapsed_mg,
            metrics=[
                response_builder.create_metric(
                    control_value=CONTROL_MEASURES_SUM,
                    test=[
                        prepare_metric(
                            response_builder.create_test_metric_values,
                        ),
                    ],
                ),
            ],
        ).build()

        assert got == expected_response

    _update_mg_version(7)
    await _invoke_cache(7)
    _update_mg_version(8)
    await _invoke_cache(8)

    assert len(mocked_web_context.chyt_clients.calls) == 2


@pytest.mark.parametrize(
    'facet_in_request,expected_facet_clause',
    [(TEST_FACET, f'`_facet` = \'{TEST_FACET}\''), (None, '`_facet` IS NULL')],
)
async def test_facet_in_request(
        abt,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        get_response_builder,
        facet_in_request,
        expected_facet_clause,
):
    state = await prepare_state()

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    request = copy.deepcopy(DEFAULT_REQUEST)
    if facet_in_request:
        request['facet'] = facet_in_request

    await invoke_handler(request, mocked_context=mocked_web_context)

    query = mocked_web_context.chyt_clients.calls[0][0]

    assert expected_facet_clause in query


VERY_LOW_SHAPIRO_THRESHOLD = '0.01'

VERY_LOW_STAT_TEST_THRESHOLD = '0.9'


@pytest.mark.config(
    ABT_CONFIDENCE_THRESHOLDS={
        app_consts.SHAPIRO_TEST_NAME: {
            'weak': VERY_LOW_SHAPIRO_THRESHOLD,
            'strong': VERY_LOW_SHAPIRO_THRESHOLD,
        },
        app_consts.TTEST_TEST_NAME: {
            'weak': VERY_LOW_STAT_TEST_THRESHOLD,
            'strong': VERY_LOW_STAT_TEST_THRESHOLD,
        },
        app_consts.MANNWHITNEYU_TEST_NAME: {
            'weak': VERY_LOW_STAT_TEST_THRESHOLD,
            'strong': VERY_LOW_STAT_TEST_THRESHOLD,
        },
    },
    ABT_HIGHLIGHT_COLORS={
        'strong/positive': {
            'background': 'background',
            'font': 'font',
            'wiki': 'wiki',
        },
    },
    ABT_COLORED_METRICS_ALIASES=['strong/positive'],
)
async def test_highlight_metrics_all_configs_work(
        invoke_handler,
        mocked_web_context,
        prepare_state,
        get_response_builder,
):
    state = await prepare_state(metric_greater_is_better=True)

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    got = await invoke_handler(
        {
            **DEFAULT_REQUEST,
            'metrics_groups': [state.collapsed_metrics_group.id],
        },
        mocked_context=mocked_web_context,
    )

    response_builder = get_response_builder(
        state.control_group, [state.test_group],
    )

    expected_response = response_builder.add_metrics_group(
        metrics_group=state.collapsed_metrics_group,
        metrics=[
            response_builder.create_metric(
                control_value=CONTROL_MEASURES_SUM,
                test=[
                    prepare_metric(
                        response_builder.create_test_metric_values,
                        is_colored=True,
                        background='background',
                        font='font',
                        color_alias='strong/positive',
                        wiki_color='wiki',
                    ),
                ],
            ),
        ],
    ).build()

    assert got == expected_response


async def test_several_metrics_groups_requested(
        abt, prepare_state, mocked_web_context, invoke_handler,
):
    state = await prepare_state()

    one_more_metrics_group = await abt.state.add_metrics_group(
        is_collapsed=False, enabled=True, config=state.metrics_config,
    )

    await abt.state.bind_mg_with_pt(
        one_more_metrics_group['id'], state.precomputes_table.id,
    )

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    got = await invoke_handler(mocked_context=mocked_web_context)

    num_computed_metrics_groups = sum(
        [1 for group in got['metrics_groups'] if not group['is_collapsed']],
    )

    assert num_computed_metrics_groups == 2
    assert len(mocked_web_context.chyt_clients.calls) == 1


@pytest.mark.parametrize(
    'expanded_position,collapsed_position,expected_order',
    [
        pytest.param(0, 100, 'expanded/collapsed'),
        pytest.param(100, 0, 'collapsed/expanded'),
    ],
)
async def test_metrics_groups_sort(
        abt,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        expanded_position,
        collapsed_position,
        expected_order,
):
    state = await prepare_state(
        expanded_position=expanded_position,
        collapsed_position=collapsed_position,
    )

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    got = await invoke_handler(
        {
            **DEFAULT_REQUEST,
            'metrics_groups': [
                state.collapsed_metrics_group.id,
                state.expanded_metrics_group.id,
            ],
        },
        mocked_context=mocked_web_context,
    )

    received_ids = [group['id'] for group in got['metrics_groups']]

    if expected_order == 'expanded/collapsed':
        expected_ids = [
            state.expanded_metrics_group.id,
            state.collapsed_metrics_group.id,
        ]
    elif expected_order == 'collapsed/expanded':
        expected_ids = [
            state.collapsed_metrics_group.id,
            state.expanded_metrics_group.id,
        ]
    else:
        assert False, f'Incorrect expected_order in params: {expected_order}'

    assert received_ids == expected_ids


async def test_metric_columns_not_in_schema(
        abt,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        get_response_builder,
):
    state = await prepare_state(
        add_collapsed=False,
        add_hidden=False,
        table_schema=abt.builders.get_pt_schema_builder().build(),
    )

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    response_builder = get_response_builder(
        state.control_group, [state.test_group],
    )

    got = await invoke_handler(mocked_context=mocked_web_context)

    expected_response = response_builder.add_metrics_group(
        metrics_group=state.expanded_metrics_group,
        metrics=[
            response_builder.create_metric(
                test=[response_builder.create_test_metric_values()],
            ),
        ],
    ).build()

    assert got == expected_response


async def test_error_while_evaluating_control_group_metric(
        abt,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        get_response_builder,
):
    state = await prepare_state(
        add_collapsed=False,
        add_hidden=False,
        table_schema=abt.builders.get_pt_schema_builder().build(),
    )

    # Do not specify control group measures -> error
    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.test_measures,
    )

    response_builder = get_response_builder(
        state.control_group, [state.test_group],
    )

    got = await invoke_handler(mocked_context=mocked_web_context)

    expected_response = response_builder.add_metrics_group(
        metrics_group=state.expanded_metrics_group,
        metrics=[
            response_builder.create_metric(
                test=[response_builder.create_test_metric_values()],
            ),
        ],
    ).build()

    assert got == expected_response


async def test_error_while_eval_one_of_groups(
        abt,
        prepare_state,
        mocked_web_context,
        invoke_handler,
        get_response_builder,
):
    state = await prepare_state(add_collapsed=False, add_hidden=False)

    one_more_metrics_group = models.MetricsGroup.from_record(
        await abt.state.add_metrics_group(
            is_collapsed=False,
            enabled=True,
            config=(
                abt.builders.get_mg_config_builder()
                # Specify column that is absent in schema -> error
                .add_value_metric(value='another_metric_column')
                .add_precomputes()
                .build()
            ),
        ),
    )

    await abt.state.bind_mg_with_pt(
        one_more_metrics_group.id, state.precomputes_table.id,
    )

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    got = await invoke_handler(mocked_context=mocked_web_context)

    response_builder = get_response_builder(
        state.control_group, [state.test_group],
    )

    expected_response = (
        response_builder.add_metrics_group(
            metrics_group=state.expanded_metrics_group,
            metrics=[
                response_builder.create_metric(
                    control_value=CONTROL_MEASURES_SUM,
                    test=[
                        prepare_metric(
                            response_builder.create_test_metric_values,
                        ),
                    ],
                ),
            ],
        )
        .add_metrics_group(
            metrics_group=one_more_metrics_group,
            metrics=[
                response_builder.create_metric(
                    test=[response_builder.create_test_metric_values()],
                ),
            ],
        )
        .build()
    )

    assert got == expected_response


async def test_if_control_value_eq_zero(
        abt,
        prepare_state,
        mocked_web_context,
        invoke_handler,
        get_response_builder,
):
    state = await prepare_state(add_collapsed=False, add_hidden=False)

    control_measures = (
        abt.builders.get_measures_builder(
            state.revision.id, state.control_group.group_id, buckets_count=10,
        )
        .add_column(consts.DEFAULT_VALUE_COLUMN, [0 for _ in range(10)])
        .build()
    )

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', control_measures + state.test_measures,
    )

    got = await invoke_handler(mocked_context=mocked_web_context)

    response_builder = get_response_builder(
        state.control_group, [state.test_group],
    )

    # If control value is zero -> relative diff == '-'
    expected_response = response_builder.add_metrics_group(
        metrics_group=state.expanded_metrics_group,
        metrics=[
            response_builder.create_metric(
                control_value='0,0',
                test=[
                    response_builder.create_test_metric_values(
                        value='145,0',
                        abs_diff='+145,0',
                        rel_diff=app_consts.METRIC_VALUE_PLACEHOLDER,
                        mannwhitneyu='0,0001',
                        shapiro='0,892',
                        ttest='0,0',
                    ),
                ],
            ),
        ],
    ).build()

    assert got == expected_response


async def test_cannot_eval_pvalues(
        abt,
        prepare_state,
        mocked_web_context,
        invoke_handler,
        get_response_builder,
):
    state = await prepare_state(
        add_collapsed=False,
        add_hidden=False,
        metrics_config=(
            abt.builders.get_mg_config_builder()
            .add_ratio_metric()
            .add_precomputes()
            .build()
        ),
        table_schema=(
            abt.builders.get_pt_schema_builder()
            .add_column(consts.DEFAULT_NUMERATOR_COLUMN)
            .add_column(consts.DEFAULT_DENOMINATOR_COLUMN)
            .build()
        ),
    )

    control_measures = (
        abt.builders.get_measures_builder(
            state.revision.id, state.control_group.group_id, buckets_count=10,
        )
        .add_column(consts.DEFAULT_NUMERATOR_COLUMN, CONTROL_MEASURES)
        .add_column(
            consts.DEFAULT_DENOMINATOR_COLUMN, [1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
        )
        .build()
    )

    # If one of value in denominator is zero we cannot compute metric
    # distribution and that's why cannot compute pvalues
    test_measures = (
        abt.builders.get_measures_builder(
            state.revision.id, state.test_group.group_id, buckets_count=10,
        )
        .add_column(consts.DEFAULT_NUMERATOR_COLUMN, CONTROL_MEASURES)
        .add_column(
            consts.DEFAULT_DENOMINATOR_COLUMN, [1, 1, 1, 1, 0, 1, 1, 1, 1, 1],
        )
        .build()
    )

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', control_measures + test_measures,
    )

    got = await invoke_handler(mocked_context=mocked_web_context)

    response_builder = get_response_builder(
        state.control_group, [state.test_group],
    )

    expected_response = response_builder.add_metrics_group(
        metrics_group=state.expanded_metrics_group,
        metrics=[
            response_builder.create_metric(
                name=consts.DEFAULT_RATIO_METRIC_NAME,
                title=consts.DEFAULT_RATIO_METRIC_TITLE,
                control_value='5,0',
                test=[
                    response_builder.create_test_metric_values(
                        value='5,0', abs_diff='0,0', rel_diff='0,0%',
                    ),
                ],
            ),
        ],
    ).build()

    assert got == expected_response


@pytest.mark.config(
    ABT_METRICS_DOCS_URL_TEMPLATE='{metrics_group_id}#{metric_name_encoded}',
)
async def test_docs_url(
        invoke_handler,
        mocked_web_context,
        prepare_state,
        get_response_builder,
):
    state = await prepare_state()

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    got = await invoke_handler(
        {
            **DEFAULT_REQUEST,
            'metrics_groups': [state.collapsed_metrics_group.id],
        },
        mocked_context=mocked_web_context,
    )

    response_builder = get_response_builder(
        state.control_group, [state.test_group],
    )

    expected_docs_url = '{metrics_group_id}#{metric_name_encoded}'.format(
        metrics_group_id=state.collapsed_metrics_group.id,
        metric_name_encoded=sphinx.to_anchor_string(
            consts.DEFAULT_VALUE_METRIC_NAME,
        ),
    )

    expected_response = response_builder.add_metrics_group(
        metrics_group=state.collapsed_metrics_group,
        metrics=[
            response_builder.create_metric(
                control_value=CONTROL_MEASURES_SUM,
                test=[
                    prepare_metric(response_builder.create_test_metric_values),
                ],
                docs_url=expected_docs_url,
            ),
        ],
    ).build()

    assert got == expected_response


async def test_taxi_exp_404(
        abt, invoke_handler, prepare_state, mocked_web_context,
):
    state = await prepare_state()

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_precomputes', state.control_measures + state.test_measures,
    )

    got = await invoke_handler(
        mocked_context=mocked_web_context,
        taxi_exp_code=404,
        taxi_exp_response={},
        expected_code=404,
    )

    assert got['code'] == app_consts.CODE_NO_REVISION_GROUP

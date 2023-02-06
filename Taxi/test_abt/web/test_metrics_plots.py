import dataclasses
import enum
import itertools
import typing as tp

import numpy as np
import pytest

from abt import consts as app_consts
from abt.api import plot_metrics
from abt.generated.service.swagger.models import api as api_models
from test_abt import consts
from test_abt.helpers import web as web_helpers


TEST_FACET = 'littlepony'

TVM_RULES = pytest.mark.config(TVM_RULES=[{'src': 'abt', 'dst': 'taxi_exp'}])


def make_request(
        plot_type: str,
        metric_name: str,
        test_experiment_groups: tp.Optional[tp.List[int]] = None,
        facet: tp.Optional[str] = None,
        revision_days: tp.Optional[tp.List[str]] = None,
) -> dict:
    body = {
        'type': plot_type,
        'experiment_groups': {
            'control': 1,
            'test': test_experiment_groups or [2],
        },
        'experiment_revision': consts.DEFAULT_REVISION_ID,
        'revision_days': (
            revision_days
            if revision_days is not None
            else consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS
        ),
        'metrics_group_id': 1,
        'metric_name': metric_name,
    }

    if facet is not None:
        body['facet'] = facet

    if plot_type == 'mde':
        body['plot_params'] = {'mde_days': 3}

    return body


@dataclasses.dataclass(frozen=True)
class State:
    plot_data: tp.List[dict]


class ValueBuildStrategy(enum.Enum):
    Default = 'default'
    Rand = 'rand'


class DateBuildStrategy(enum.Enum):
    Default = 'default'
    Empty = 'empty'


@pytest.fixture(name='prepare_state')
async def prepare_state_fixture(abt):
    async def _inner(
            metric_greater_is_better=None,
            collapsed_position=consts.DEFAULT_METRICS_GROUP_POSITION,
            expanded_position=consts.DEFAULT_METRICS_GROUP_POSITION,
            partial_plot_data=False,
            data_available_days=None,
            buckets=2,
            value_strategy=ValueBuildStrategy.Default,
            date_strategy=DateBuildStrategy.Default,
            groups=2,
    ):
        metrics_config = (
            abt.builders.get_mg_config_builder()
            .add_value_metric(greater_is_better=metric_greater_is_better)
            .add_ratio_metric(greater_is_better=metric_greater_is_better)
            .add_precomputes()
            .build()
        )
        collapsed_metrics_group = await abt.state.add_metrics_group(
            is_collapsed=True,
            enabled=False,
            config=metrics_config,
            position=collapsed_position,
        )
        expanded_metrics_group = await abt.state.add_metrics_group(
            is_collapsed=False,
            enabled=True,
            config=metrics_config,
            position=expanded_position,
        )
        precomputes_table = await abt.state.add_precomputes_table(
            schema=abt.builders.get_pt_schema_builder()
            .add_column(consts.DEFAULT_VALUE_COLUMN)
            .add_column(consts.DEFAULT_NUMERATOR_COLUMN)
            .add_column(consts.DEFAULT_DENOMINATOR_COLUMN)
            .build(),
        )
        experiment = await abt.state.add_experiment()

        await abt.state.bind_mg_with_pt(
            collapsed_metrics_group['id'], precomputes_table['id'],
        )
        await abt.state.bind_mg_with_pt(
            expanded_metrics_group['id'], precomputes_table['id'],
        )
        await abt.state.bind_pt_with_experiment(
            precomputes_table['id'], experiment['id'],
        )

        data_available_days = (
            data_available_days
            if data_available_days
            else consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS
        )
        revision = await abt.state.add_revision(
            data_available_days=data_available_days,
        )

        await abt.state.add_facets(
            TEST_FACET, precomputes_table['id'], revision['revision_id'],
        )

        plot_data_builder = abt.builders.get_plot_data_builder()
        for date in (
                data_available_days
                if date_strategy == DateBuildStrategy.Default
                else [None]
        ):
            for bucket, group_id in itertools.product(
                    range(buckets), range(groups),
            ):
                if value_strategy == ValueBuildStrategy.Default:
                    plot_data_builder.add_column(
                        consts.DEFAULT_VALUE_COLUMN,
                        group_id=group_id + 1,
                        bucket=bucket,
                        value=group_id + bucket + 2,
                        date=date,
                    )
                    plot_data_builder.add_column(
                        consts.DEFAULT_NUMERATOR_COLUMN,
                        group_id=group_id + 1,
                        bucket=bucket,
                        value=group_id + bucket + 3,
                        date=date,
                    )
                    plot_data_builder.add_column(
                        consts.DEFAULT_DENOMINATOR_COLUMN,
                        group_id=group_id + 1,
                        bucket=bucket,
                        value=group_id + 4,
                        date=date,
                    )
                elif value_strategy == ValueBuildStrategy.Rand:
                    plot_data_builder.add_column(
                        consts.DEFAULT_VALUE_COLUMN,
                        group_id=group_id + 1,
                        bucket=bucket,
                        value=np.random.binomial(
                            n=1, p=0.5 if group_id == 0 else 0.6,
                        ),
                        date=date,
                    )
                    plot_data_builder.add_column(
                        consts.DEFAULT_NUMERATOR_COLUMN,
                        group_id=group_id + 1,
                        bucket=bucket,
                        value=np.random.binomial(
                            n=1000, p=0.5 if group_id == 0 else 0.9,
                        ),
                        date=date,
                    )
                    plot_data_builder.add_column(
                        consts.DEFAULT_DENOMINATOR_COLUMN,
                        group_id=group_id + 1,
                        bucket=bucket,
                        value=1,
                        date=date,
                    )
        if partial_plot_data:
            for bucket in range(2):
                plot_data_builder.remove_column(
                    col_name=consts.DEFAULT_VALUE_COLUMN,
                    date=consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS[0],
                    bucket=bucket,
                    group_id=1,
                )
                plot_data_builder.remove_column(
                    col_name=consts.DEFAULT_DENOMINATOR_COLUMN,
                    date=consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS[0],
                    bucket=bucket,
                    group_id=1,
                )
                plot_data_builder.remove_column(
                    col_name=consts.DEFAULT_DENOMINATOR_COLUMN,
                    date=consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS[1],
                    bucket=bucket,
                    group_id=2,
                )

        return State(plot_data=plot_data_builder.build())

    return _inner


@pytest.fixture(name='invoke_handler')
def _invoke_handler(taxi_abt_web, mocked_web_request, mockserver, load_json):
    async def _inner(
            body,
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
                'post', '/v1/metrics/plot', taxi_abt_web,
            )(body=body, expected_code=expected_code)

        async def _mock_req_func(endpoint, **kwargs):
            return await plot_metrics.handle(
                mocked_web_request(
                    api_models.PlotMetricsRequest.deserialize(kwargs['json']),
                ),
                mocked_context,
            )

        async def _mock_resp_parser(response):
            return response.data.serialize()

        return await web_helpers.create_invoke(
            'post',
            '/v1/metrics/plot',
            taxi_abt_web,
            req_func=_mock_req_func,
            resp_parser=_mock_resp_parser,
        )(body=body, expected_code=expected_code)

    return _inner


@pytest.mark.parametrize(
    'plot_type,metric_name,data_available_days,'
    'buckets,value_strategy,date_strategy,filename',
    [
        (
            'absolute',
            consts.DEFAULT_VALUE_METRIC_NAME,
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            2,
            ValueBuildStrategy.Default,
            DateBuildStrategy.Default,
            'test_metrics_abs_plot_value_response.json',
        ),
        (
            'absolute',
            consts.DEFAULT_RATIO_METRIC_NAME,
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            2,
            ValueBuildStrategy.Default,
            DateBuildStrategy.Default,
            'test_metrics_abs_plot_ratio_response.json',
        ),
        (
            'hist',
            consts.DEFAULT_VALUE_METRIC_NAME,
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            2,
            ValueBuildStrategy.Default,
            DateBuildStrategy.Default,
            'test_metrics_hist_plot_value_response.json',
        ),
        (
            'hist',
            consts.DEFAULT_RATIO_METRIC_NAME,
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            2,
            ValueBuildStrategy.Default,
            DateBuildStrategy.Default,
            'test_metrics_hist_plot_ratio_response.json',
        ),
        (
            'conf_int',
            consts.DEFAULT_VALUE_METRIC_NAME,
            consts.EXTENDED_REVISION_DATA_AVAILABLE_DAYS,
            100,
            ValueBuildStrategy.Rand,
            DateBuildStrategy.Default,
            'test_metrics_conf_int_plot_value_response.json',
        ),
        (
            'conf_int',
            consts.DEFAULT_RATIO_METRIC_NAME,
            consts.EXTENDED_REVISION_DATA_AVAILABLE_DAYS,
            100,
            ValueBuildStrategy.Rand,
            DateBuildStrategy.Default,
            'test_metrics_conf_int_plot_ratio_response.json',
        ),
        (
            'mde',
            consts.DEFAULT_VALUE_METRIC_NAME,
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            100,
            ValueBuildStrategy.Rand,
            DateBuildStrategy.Empty,
            'test_metrics_mde_plot_value_response.json',
        ),
        (
            'mde',
            consts.DEFAULT_RATIO_METRIC_NAME,
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            100,
            ValueBuildStrategy.Rand,
            DateBuildStrategy.Empty,
            'test_metrics_mde_plot_ratio_response.json',
        ),
    ],
)
async def test_plot_ok(
        invoke_handler,
        mocked_web_context,
        prepare_state,
        plot_type,
        metric_name,
        data_available_days,
        buckets,
        value_strategy,
        date_strategy,
        filename,
        load_json,
):
    np.random.seed(8)

    state = await prepare_state(
        data_available_days=data_available_days,
        buckets=buckets,
        value_strategy=value_strategy,
        date_strategy=date_strategy,
    )

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_plots_precomputes', state.plot_data,
    )

    got = await invoke_handler(
        make_request(
            plot_type, metric_name, revision_days=data_available_days,
        ),
        mocked_context=mocked_web_context,
    )
    assert got == load_json(filename)


@pytest.mark.parametrize(
    'plot_type,data_available_days,buckets,'
    'value_strategy,date_strategy,filename',
    [
        (
            'absolute',
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            2,
            ValueBuildStrategy.Default,
            DateBuildStrategy.Default,
            'test_metrics_abs_plot_value_response.json',
        ),
        (
            'hist',
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            2,
            ValueBuildStrategy.Default,
            DateBuildStrategy.Default,
            'test_metrics_hist_plot_value_response.json',
        ),
        (
            'conf_int',
            consts.EXTENDED_REVISION_DATA_AVAILABLE_DAYS,
            100,
            ValueBuildStrategy.Rand,
            DateBuildStrategy.Default,
            'test_metrics_conf_int_plot_value_response.json',
        ),
        (
            'mde',
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            100,
            ValueBuildStrategy.Rand,
            DateBuildStrategy.Empty,
            'test_metrics_mde_plot_value_response.json',
        ),
    ],
)
@pytest.mark.config(
    ABT_RESPONSES_CACHE={
        'enabled': True,
        'handles_settings': [
            {'uri': '/v1/metrics/plot', 'item_life_time': 604800},
        ],
    },
)
async def test_using_cache_simple(
        abt,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        plot_type,
        data_available_days,
        buckets,
        value_strategy,
        date_strategy,
        filename,
        load_json,
):
    np.random.seed(8)

    state = await prepare_state(
        data_available_days=data_available_days,
        buckets=buckets,
        value_strategy=value_strategy,
        date_strategy=date_strategy,
    )

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_plots_precomputes', state.plot_data,
    )

    for _ in range(2):
        got = await invoke_handler(
            make_request(
                plot_type,
                consts.DEFAULT_VALUE_METRIC_NAME,
                revision_days=data_available_days,
            ),
            mocked_context=mocked_web_context,
        )

        assert got == load_json(filename)

    assert len(mocked_web_context.chyt_clients.calls) == 1


@pytest.mark.parametrize(
    'plot_type,data_available_days,buckets,value_strategy,date_strategy',
    [
        (
            'absolute',
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            2,
            ValueBuildStrategy.Default,
            DateBuildStrategy.Default,
        ),
        (
            'hist',
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            2,
            ValueBuildStrategy.Default,
            DateBuildStrategy.Default,
        ),
        (
            'conf_int',
            consts.EXTENDED_REVISION_DATA_AVAILABLE_DAYS,
            100,
            ValueBuildStrategy.Rand,
            DateBuildStrategy.Default,
        ),
        (
            'mde',
            consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            100,
            ValueBuildStrategy.Rand,
            DateBuildStrategy.Empty,
        ),
    ],
)
@pytest.mark.config(
    ABT_RESPONSES_CACHE={
        'enabled': True,
        'handles_settings': [
            {'uri': '/v1/metrics/plot', 'item_life_time': 604800},
        ],
    },
)
async def test_caching_all_revision_groups(
        abt,
        invoke_handler,
        mocked_web_context,
        prepare_state,
        plot_type,
        data_available_days,
        buckets,
        value_strategy,
        date_strategy,
        load_json,
):
    state = await prepare_state(
        data_available_days=data_available_days,
        buckets=buckets,
        value_strategy=value_strategy,
        date_strategy=date_strategy,
        groups=3,
    )

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_plots_precomputes', state.plot_data,
    )

    await invoke_handler(
        make_request(
            plot_type,
            consts.DEFAULT_VALUE_METRIC_NAME,
            test_experiment_groups=[2],
            revision_days=data_available_days,
        ),
        mocked_context=mocked_web_context,
    )

    second_resp = await invoke_handler(
        make_request(
            plot_type,
            consts.DEFAULT_VALUE_METRIC_NAME,
            test_experiment_groups=[3],
            revision_days=data_available_days,
        ),
        mocked_context=mocked_web_context,
    )

    for point in second_resp['data']:
        if plot_type == 'hist':
            assert point['group_id'] in [1, 3]
            continue
        for value in point['values']:
            assert value['group_id'] in [1, 3]

    assert len(mocked_web_context.chyt_clients.calls) == 1


@pytest.mark.config(
    ABT_RESPONSES_CACHE={
        'enabled': True,
        'handles_settings': [
            {'uri': '/v1/metrics/plot', 'item_life_time': 604800},
        ],
    },
)
async def test_recache_if_metrics_group_is_obsolete(
        abt, pgsql, invoke_handler, mocked_web_context, prepare_state,
):
    np.random.seed(8)

    state = await prepare_state(
        data_available_days=consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
        buckets=2,
        value_strategy=ValueBuildStrategy.Default,
        date_strategy=DateBuildStrategy.Default,
    )

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_plots_precomputes', state.plot_data,
    )

    def _update_mg_version(mg_version):
        cursor = pgsql['abt'].cursor()
        cursor.execute(
            f'UPDATE abt.metrics_groups ' f'SET version={mg_version}',
        )
        cursor.close()

    async def _invoke_handler():
        await invoke_handler(
            make_request(
                'hist',
                consts.DEFAULT_VALUE_METRIC_NAME,
                revision_days=consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS,
            ),
            mocked_context=mocked_web_context,
        )

    _update_mg_version(7)
    await _invoke_handler()
    _update_mg_version(8)
    await _invoke_handler()

    assert len(mocked_web_context.chyt_clients.calls) == 2


@pytest.mark.parametrize(
    'plot_type,metric_name,filename',
    [
        (
            'absolute',
            consts.DEFAULT_RATIO_METRIC_NAME,
            'test_group_eval_error_absolute_plot_ratio_response.json',
        ),
    ],
)
async def test_group_eval_error(
        prepare_state,
        invoke_handler,
        mocked_web_context,
        plot_type,
        metric_name,
        filename,
        load_json,
):
    state = await prepare_state(partial_plot_data=True)

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_plots_precomputes', state.plot_data,
    )

    got = await invoke_handler(
        make_request(plot_type, metric_name),
        mocked_context=mocked_web_context,
    )

    assert got == load_json(filename)


@pytest.mark.parametrize(
    'facet,expected_query',
    [
        pytest.param(
            None,
            (
                'SELECT `group`,`date`,sum(`default_value_column`) '
                'AS default_value_column '
                'FROM `//home/testsuite/precomputes[1]` '
                'PREWHERE `revision` = 1 AND '
                '`date` IN (\'2020-09-03\',\'2020-10-20\') '
                'AND `_facet` IS NULL '
                'AND `group` IN (1,2) '
                'GROUP BY `group`,`date` ORDER BY `group`,`date`'
            ),
            id='facet is null',
        ),
        pytest.param(
            TEST_FACET,
            (
                f'SELECT `group`,`date`,sum(`default_value_column`) '
                f'AS default_value_column '
                f'FROM `//home/testsuite/precomputes[1]` '
                f'PREWHERE `revision` = 1 AND '
                f'`date` IN (\'2020-09-03\',\'2020-10-20\') '
                f'AND `_facet` = \'{TEST_FACET}\' '
                f'AND `group` IN (1,2) '
                f'GROUP BY `group`,`date` ORDER BY `group`,`date`'
            ),
            id='facet == some value',
        ),
    ],
)
async def test_query_with_facet(
        invoke_handler,
        mocked_web_context,
        prepare_state,
        facet,
        expected_query,
):
    state = await prepare_state()

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_plots_precomputes', state.plot_data,
    )

    await invoke_handler(
        make_request(
            'absolute', consts.DEFAULT_VALUE_METRIC_NAME, facet=facet,
        ),
        mocked_context=mocked_web_context,
    )

    query, _, _ = mocked_web_context.chyt_clients.calls[0]

    assert query == expected_query


async def test_taxi_exp_404(invoke_handler, prepare_state, mocked_web_context):
    state = await prepare_state()

    mocked_web_context.chyt_clients.set_mock_response(
        'fetch_plots_precomputes', state.plot_data,
    )

    got = await invoke_handler(
        make_request(
            'absolute', consts.DEFAULT_VALUE_METRIC_NAME, facet=TEST_FACET,
        ),
        mocked_context=mocked_web_context,
        taxi_exp_code=404,
        taxi_exp_response={},
        expected_code=404,
    )

    assert got['code'] == app_consts.CODE_NO_REVISION_GROUP

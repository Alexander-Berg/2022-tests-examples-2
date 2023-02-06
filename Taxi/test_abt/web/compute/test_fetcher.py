import numpy as np
import pytest

from abt import models
from abt.repositories import storage as storage_module
from abt.repositories import yt as yt_repos
from abt.services import metrics_data_manager as metrics_data_manager_service
from abt.services.compute import fetcher as fetcher_module
from test_abt import consts


DEFAULT_VALUE_MEASURES = list(range(10))


DEFAULT_DENOMINATOR_MEASURES = list(range(10, 20))


DEFAULT_NUMERATOR_MEASURES = list(range(20, 30))


@pytest.fixture(name='prepare_state')
async def prepared_state_fixture(web_context, abt, chyt_clients_mock):
    async def _inner(fetcher_cls=None):
        precomputes_table = await abt.state.add_precomputes_table(
            schema=abt.builders.get_pt_schema_builder()
            .add_column(consts.DEFAULT_VALUE_COLUMN)
            .add_column(consts.DEFAULT_NUMERATOR_COLUMN)
            .add_column(consts.DEFAULT_DENOMINATOR_COLUMN)
            .build(),
        )
        metrics_group = models.MetricsGroup.from_record(
            await abt.state.add_metrics_group(
                is_collapsed=False,
                enabled=True,
                config=abt.builders.get_mg_config_builder()
                .add_value_metric()
                .add_ratio_metric()
                .add_precomputes()
                .build(),
            ),
        )
        await abt.state.bind_mg_with_pt(
            metrics_group.id, precomputes_table['id'],
        )
        experiment = models.Experiment.from_record(
            await abt.state.add_experiment(),
        )
        await abt.state.bind_pt_with_experiment(
            precomputes_table['id'], experiment.id,
        )
        revision = models.Revision.from_record(await abt.state.add_revision())

        data_manager = metrics_data_manager_service.MetricsDataManager(
            storage_module.from_context(web_context),
        )

        await data_manager.init(experiment)

        if fetcher_cls is None:
            fetcher_cls = fetcher_module.MetricsFetcher

        if fetcher_cls == fetcher_module.MetricsFetcher:
            fetcher = fetcher_cls(
                yt_repos.PrecomputesTablesRepository(
                    chyt_clients_mock,
                    web_context.yt_queries,
                    web_context.config,
                ),
                data_manager,
                revision,
                10,
                [20, 21],
                revision.data_available_days,
                None,
            )
        else:
            metric = metrics_group.get_metric_by_name(
                consts.DEFAULT_VALUE_METRIC_NAME,
            )

            fetcher = fetcher_cls(
                yt_repos.PrecomputesTablesRepository(
                    chyt_clients_mock,
                    web_context.yt_queries,
                    web_context.config,
                ),
                data_manager,
                metric,
                revision,
                10,
                [20, 21],
                revision.data_available_days,
                None,
            )

        return (fetcher, data_manager, 10, [20, 21], revision, metrics_group)

    return _inner


async def test_built_query(prepare_state, chyt_clients_mock):
    (fetcher, _, _, _, revision, _) = await prepare_state()

    chyt_clients_mock.set_mock_response(
        query_name='fetch_precomputes', response=[],
    )

    await fetcher.fetch()

    assert len(chyt_clients_mock.calls) == 1

    executed_query = chyt_clients_mock.calls[0][0]

    assert executed_query == (
        'SELECT `group`,`bucket`,'
        'sum(`default_denominator_column`) AS default_denominator_column,'
        'sum(`default_numerator_column`) AS default_numerator_column,'
        'sum(`default_value_column`) AS default_value_column '
        f'FROM `//home/testsuite/precomputes[{revision.id}]` '
        f'PREWHERE `revision` = {revision.id} '
        'AND `date` IN (\'2020-09-03\',\'2020-10-20\') '
        'AND `_facet` IS NULL '
        'AND `group` IN (10,20,21) '
        'GROUP BY `group`,`bucket` '
        'ORDER BY `group`,`bucket`'
    )


@pytest.mark.parametrize(
    'fetcher_cls,aggregation_field',
    [
        (fetcher_module.AbsolutePlotDataFetcher, 'date'),
        (fetcher_module.HistPlotDataFetcher, 'bucket'),
    ],
)
async def test_built_query_plot_data_fetcher(
        abt, prepare_state, chyt_clients_mock, fetcher_cls, aggregation_field,
):
    (
        fetcher,
        _,
        control_group_id,
        test_groups_ids,
        _,
        _,
    ) = await prepare_state(fetcher_cls=fetcher_cls)

    plot_data_builder = abt.builders.get_plot_data_builder()

    for date in consts.DEFAULT_REVISION_DATA_AVAILABLE_DAYS:
        for group_id in [control_group_id] + test_groups_ids:
            plot_data_builder.add_column(
                consts.DEFAULT_VALUE_COLUMN,
                date=date,
                group_id=group_id,
                bucket=50,
                value=group_id + 10,  # some value
            )

    chyt_clients_mock.set_mock_response(
        query_name='fetch_plots_precomputes',
        response=plot_data_builder.build(),
    )

    await fetcher.fetch()

    assert len(chyt_clients_mock.calls) == 1

    executed_query = chyt_clients_mock.calls[0][0]

    assert executed_query == (
        f'SELECT `group`,`{aggregation_field}`,'
        'sum(`default_value_column`) AS default_value_column '
        'FROM `//home/testsuite/precomputes[1]` '
        'PREWHERE `revision` = 1 '
        'AND `date` IN (\'2020-09-03\',\'2020-10-20\') '
        'AND `_facet` IS NULL '
        'AND `group` IN (10,20,21) '
        f'GROUP BY `group`,`{aggregation_field}` '
        f'ORDER BY `group`,`{aggregation_field}`'
    )


async def test_measures(abt, prepare_state, chyt_clients_mock):
    (
        fetcher,
        data_manager,
        control_group_id,
        _,
        revision,
        _,
    ) = await prepare_state()

    chyt_clients_mock.set_mock_response(
        query_name='fetch_precomputes',
        response=(
            abt.builders.get_measures_builder(
                revision.id, control_group_id, buckets_count=10,
            )
            .add_column(consts.DEFAULT_VALUE_COLUMN, DEFAULT_VALUE_MEASURES)
            .add_column(
                consts.DEFAULT_NUMERATOR_COLUMN, DEFAULT_NUMERATOR_MEASURES,
            )
            .add_column(
                consts.DEFAULT_DENOMINATOR_COLUMN,
                DEFAULT_DENOMINATOR_MEASURES,
            )
            .build()
        ),
    )

    precomputes_table = data_manager.precomputes_tables[0]

    measures = await fetcher.fetch()

    assert len(chyt_clients_mock.calls) == 1

    group_measures = measures.for_key(precomputes_table.id).for_group(
        control_group_id,
    )

    for col, col_measures in [
            (consts.DEFAULT_VALUE_COLUMN, DEFAULT_VALUE_MEASURES),
            (consts.DEFAULT_NUMERATOR_COLUMN, DEFAULT_NUMERATOR_MEASURES),
            (consts.DEFAULT_DENOMINATOR_COLUMN, DEFAULT_DENOMINATOR_MEASURES),
    ]:
        np.testing.assert_array_equal(
            group_measures.for_measure_as_ndarray(col), np.array(col_measures),
        )


async def test_different_number_of_buckets(
        abt, chyt_clients_mock, prepare_state,
):
    (
        fetcher,
        data_manager,
        control_group_id,
        test_groups_ids,
        revision,
        _,
    ) = await prepare_state()

    control_group_data = (
        abt.builders.get_measures_builder(
            revision.id, control_group_id, buckets_count=10,
        )
        .add_column(consts.DEFAULT_VALUE_COLUMN, range(10))
        .build()
    )

    test_group_id = test_groups_ids[0]

    test_group_data = (
        abt.builders.get_measures_builder(
            revision.id, test_group_id, buckets_count=20,
        )
        .add_column(consts.DEFAULT_VALUE_COLUMN, range(20))
        .build()
    )

    response_data = control_group_data + test_group_data

    chyt_clients_mock.set_mock_response(
        query_name='fetch_precomputes', response=response_data,
    )

    measures = await fetcher.fetch()

    assert len(chyt_clients_mock.calls) == 1

    precomputes_table = data_manager.precomputes_tables[0]

    assert (
        measures.for_key(precomputes_table.id)
        .for_group(control_group_id)
        .for_measure(consts.DEFAULT_VALUE_COLUMN)
    ) == list(range(10))

    assert (
        measures.for_key(precomputes_table.id)
        .for_group(test_group_id)
        .for_measure(consts.DEFAULT_VALUE_COLUMN)
    ) == list(range(20))

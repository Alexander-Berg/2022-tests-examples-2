import dataclasses

import pytest

from abt import models
from abt.repositories import storage as storage_module
from abt.services import metrics_data_manager as metrics_data_manager_service
from abt.utils import exceptions
from test_abt import consts


async def test_get_metrics_fields(abt, web_context):
    config_builder = abt.builders.get_mg_config_builder()
    config_builder.add_value_metric(value='test_value_column')
    config_builder.add_ratio_metric(
        numerator='test_ratio_numerator',
        denominator='test_ration_denominator',
    )
    config_builder.add_precomputes()  # for correct config

    #

    metrics_group = models.MetricsGroup.from_record(
        await abt.state.add_metrics_group(config=config_builder.build()),
    )

    #

    assert metrics_group.get_metrics_fields() == {
        'test_value_column',
        'test_ratio_numerator',
        'test_ration_denominator',
    }


@dataclasses.dataclass(frozen=True)
class State:
    precomputes_table: models.PrecomputesTable
    metrics_config: dict
    metrics_group_collapsed: models.MetricsGroup
    metrics_group_expanded: models.MetricsGroup
    experiment: models.Experiment
    revision: models.Revision
    manager: metrics_data_manager_service.MetricsDataManager


@pytest.fixture(name='prepare_state')
async def prepare_state_fixture(abt, web_context):
    async def _inner():
        precomputes_table = models.PrecomputesTable.from_record(
            await abt.state.add_precomputes_table(
                schema=abt.builders.get_pt_schema_builder()
                .add_column(consts.DEFAULT_VALUE_COLUMN)
                .add_column(consts.DEFAULT_NUMERATOR_COLUMN)
                .add_column(consts.DEFAULT_DENOMINATOR_COLUMN)
                .build(),
            ),
        )
        metrics_group_collapsed = models.MetricsGroup.from_record(
            await abt.state.add_metrics_group(is_collapsed=True, enabled=True),
        )
        metrics_config = (
            abt.builders.get_mg_config_builder()
            .add_value_metric()
            .add_ratio_metric()
            .add_precomputes()
            .build()
        )
        metrics_group_expanded = models.MetricsGroup.from_record(
            await abt.state.add_metrics_group(
                is_collapsed=False, enabled=True, config=metrics_config,
            ),
        )
        experiment = models.Experiment.from_record(
            await abt.state.add_experiment(),
        )
        revision = models.Revision.from_record(await abt.state.add_revision())

        await abt.state.bind_mg_with_pt(
            metrics_group_collapsed.id, precomputes_table.id,
        )
        await abt.state.bind_mg_with_pt(
            metrics_group_expanded.id, precomputes_table.id,
        )
        await abt.state.bind_pt_with_experiment(
            precomputes_table.id, experiment.id,
        )

        manager = metrics_data_manager_service.MetricsDataManager(
            storage_module.from_context(web_context),
        )

        return State(
            precomputes_table=precomputes_table,
            metrics_config=metrics_config,
            metrics_group_collapsed=metrics_group_collapsed,
            metrics_group_expanded=metrics_group_expanded,
            experiment=experiment,
            revision=revision,
            manager=manager,
        )

    return _inner


async def test_precomputes_tables_property(prepare_state):
    state = await prepare_state()
    await state.manager.init(state.revision)

    assert [table.id for table in state.manager.precomputes_tables] == [
        state.precomputes_table.id,
    ]


async def test_metrics_groups_property(prepare_state):
    state = await prepare_state()
    await state.manager.init(state.revision)

    assert (
        sorted(group.id for group in state.manager.metrics_groups)
        == sorted(
            [
                state.metrics_group_collapsed.id,
                state.metrics_group_expanded.id,
            ],
        )
    )


async def test_metrics_groups_to_compute_property(prepare_state):
    state = await prepare_state()
    await state.manager.init(state.revision)

    expected_mg_ids_to_compute = [
        state.metrics_group_expanded.id,
        state.metrics_group_collapsed.id,
    ]

    assert sorted(
        group.id for group in state.manager.metrics_groups_to_compute
    ) == sorted(expected_mg_ids_to_compute)


async def test_init_with_facet(abt, prepare_state):
    state = await prepare_state()

    another_precomputes_table = models.PrecomputesTable.from_record(
        await abt.state.add_precomputes_table(
            yt_path='//some/good/path',
            schema=abt.builders.get_pt_schema_builder()
            .add_column(consts.DEFAULT_VALUE_COLUMN)
            .add_column(consts.DEFAULT_NUMERATOR_COLUMN)
            .add_column(consts.DEFAULT_DENOMINATOR_COLUMN)
            .build(),
        ),
    )

    await abt.state.bind_mg_with_pt(
        state.metrics_group_collapsed.id, another_precomputes_table.id,
    )
    await abt.state.bind_pt_with_experiment(
        another_precomputes_table.id, state.experiment.id,
    )

    await abt.state.add_facets(
        'littlefacet', another_precomputes_table.id, state.revision.id,
    )

    await state.manager.init(state.revision, facet='littlefacet')

    expected_mg_ids_to_compute = [state.metrics_group_collapsed.id]

    assert sorted(
        group.id for group in state.manager.metrics_groups_to_compute
    ) == sorted(expected_mg_ids_to_compute)


async def test_metrics_groups_not_to_compute_property(prepare_state):
    state = await prepare_state()
    await state.manager.init(
        state.revision, [state.metrics_group_collapsed.id],
    )

    expected_mg_ids_not_to_compute = [state.metrics_group_expanded.id]

    assert sorted(
        group.id for group in state.manager.metrics_groups_not_to_compute
    ) == sorted(expected_mg_ids_not_to_compute)


async def test_precomputes_tables_to_fetch_property(abt, prepare_state):
    state = await prepare_state()

    one_more_metrics_group = await abt.state.add_metrics_group(
        is_collapsed=False, enabled=True, config=state.metrics_config,
    )

    await abt.state.bind_mg_with_pt(
        one_more_metrics_group['id'], state.precomputes_table.id,
    )

    await state.manager.init(state.revision)

    assert [
        table.id for table in state.manager.precomputes_tables_to_fetch
    ] == [state.precomputes_table.id]


async def test_related_precomputes_tables_method(prepare_state):
    state = await prepare_state()
    await state.manager.init(state.revision)

    assert [
        table.id
        for table in state.manager.related_precomputes_tables(
            state.metrics_group_collapsed,
        )
    ] == [state.precomputes_table.id]


async def test_fields_to_select_method(prepare_state):
    state = await prepare_state()
    await state.manager.init(state.revision)

    expected_fields_to_select = sorted(
        state.metrics_group_expanded.get_metrics_fields(),
    )

    assert (
        sorted(state.manager.fields_to_select(state.precomputes_table))
        == expected_fields_to_select
    )


@pytest.mark.parametrize(
    'requested_metrics_groups',
    [
        pytest.param('none', id='No metrics groups requested -> all fetched'),
        pytest.param('one', id='One metrics group requested'),
        pytest.param('many', id='Some metrics groups requested'),
        pytest.param('absent', id='absent metrics group requested'),
    ],
)
async def test_different_requested_metrics_groups(
        abt, web_context, requested_metrics_groups,
):
    precomputes_table = await abt.state.add_precomputes_table()
    metrics_groups = [await abt.state.add_metrics_group() for _ in range(3)]
    experiment = models.Experiment.from_record(
        await abt.state.add_experiment(),
    )
    revision = models.Revision.from_record(await abt.state.add_revision())

    for metrics_group in metrics_groups:
        await abt.state.bind_mg_with_pt(
            metrics_group['id'], precomputes_table['id'],
        )

    await abt.state.bind_pt_with_experiment(
        precomputes_table['id'], experiment.id,
    )

    manager = metrics_data_manager_service.MetricsDataManager(
        storage_module.from_context(web_context),
    )

    #

    if requested_metrics_groups == 'absent':
        with pytest.raises(exceptions.IncompleteResults):
            await manager.init(revision, [100500])
    elif requested_metrics_groups == 'none':
        await manager.init(revision)
        assert [
            group.id for group in manager.metrics_groups_not_to_compute
        ] == []
        assert sorted(
            group.id for group in manager.metrics_groups_to_compute
        ) == sorted(group['id'] for group in metrics_groups)
    elif requested_metrics_groups == 'one':
        await manager.init(revision, [metrics_groups[0]['id']])
        assert sorted(
            group.id for group in manager.metrics_groups_to_compute
        ) == [metrics_groups[0]['id']]
        assert sorted(
            group.id for group in manager.metrics_groups_not_to_compute
        ) == sorted(group['id'] for group in metrics_groups[1:])
    elif requested_metrics_groups == 'many':
        await manager.init(
            revision, [group['id'] for group in metrics_groups[1:]],
        )
        assert sorted(
            group.id for group in manager.metrics_groups_to_compute
        ) == sorted(group['id'] for group in metrics_groups[1:])
        assert sorted(
            group.id for group in manager.metrics_groups_not_to_compute
        ) == [metrics_groups[0]['id']]
    else:
        raise NotImplementedError

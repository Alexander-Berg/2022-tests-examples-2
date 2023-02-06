# flake8: noqa: E501
import functools

import pytest

import eventus_orchestrator.common.configuration.remove_named_groups as remove_named_groups
import eventus_orchestrator.generated.service.swagger.models.api as gen_api

_ARG_MAP_TEST = gen_api.ArgumentsMap({'field_1': 'field_value'})
_ERROR_HANDLING_POLICY = gen_api.ErrorHandlingPolicy(
    retry_policy=gen_api.RetryPolicy(
        attempts=3, min_delay_ms=10, max_delay_ms=50, delay_factor=2,
    ),
    action_after_erroneous_execution='propagate',
)


def _get_operation_list(list_output, length):
    operation_variants = [
        gen_api.Operation(
            operation_name=f'filter_name_66{i}',
            type='mapper',
            arguments=_ARG_MAP_TEST,
        )
        for i in range(length)
    ]

    operations = [
        gen_api.OperationNodeBody(
            name=f'filter_66{i}',
            is_disabled=False,
            operation_variant=op_var,
            error_handling_policy=_ERROR_HANDLING_POLICY,
        )
        for i, op_var in enumerate(operation_variants)
    ]

    op_list = gen_api.OperationList(operations=operations, output=list_output)

    return op_list


def _make_with_named_group(operation_list, fst_index, lst_index):
    name = f'named_group_{fst_index}_{lst_index}'
    named_list_operations = operation_list.operations[fst_index:lst_index]
    del operation_list.operations[fst_index:lst_index]

    named_op_list = gen_api.NamedOperationList(
        operations=named_list_operations, name=name,
    )

    operation_list.operations.insert(fst_index, named_op_list)
    return operation_list


def _get_operation_list_with_group(list_output, length, fst_index, lst_index):
    return _make_with_named_group(
        _get_operation_list(list_output, length), fst_index, lst_index,
    )


def get_test_pipeline(get_op_list_func, op_lists_length):
    pipeline_name = 'test'

    sink_1 = gen_api.Sink(
        sink_name='sink_name_1',
        arguments=_ARG_MAP_TEST,
        error_handling_policy=_ERROR_HANDLING_POLICY,
    )

    sink_2 = gen_api.Sink(
        sink_name='sink_name_2',
        arguments=_ARG_MAP_TEST,
        error_handling_policy=_ERROR_HANDLING_POLICY,
    )

    sink_3 = gen_api.Sink(
        sink_name='sink_name_3',
        arguments=_ARG_MAP_TEST,
        error_handling_policy=_ERROR_HANDLING_POLICY,
    )

    sink_4 = gen_api.Sink(
        sink_name='sink_name_4',
        arguments=_ARG_MAP_TEST,
        error_handling_policy=_ERROR_HANDLING_POLICY,
    )

    fanout_1 = gen_api.FanOut([sink_1, sink_2])
    fanout_2 = gen_api.FanOut([sink_3, sink_4])

    node_list_2 = get_op_list_func(fanout_1, op_lists_length)
    node_list_3 = get_op_list_func(fanout_2, op_lists_length)

    fanout_3 = gen_api.FanOut([node_list_3, node_list_2])

    node_list_1 = get_op_list_func(fanout_3, op_lists_length)

    pipeline = gen_api.PipelineConfiguration(
        description='description',
        is_disabled=False,
        st_ticket='st_ticket',
        source=gen_api.Source(name=pipeline_name, arguments=_ARG_MAP_TEST),
        root=node_list_1,
    )
    return pipeline


@pytest.mark.parametrize(
    'group_len, fst_index, lst_index',
    [
        (gl, fst, lst)
        for gl in range(1, 5)
        for fst in range(0, gl)
        for lst in range(fst, gl + 1)
    ],
)
async def test_group_of_ops_remove(group_len, fst_index, lst_index):
    pipeline = get_test_pipeline(
        functools.partial(
            _get_operation_list_with_group,
            fst_index=fst_index,
            lst_index=lst_index,
        ),
        group_len,
    )
    pipeline_wo_named_groups = get_test_pipeline(
        _get_operation_list, group_len,
    )
    remove_named_groups.remove_named_groups(pipeline)
    assert pipeline.serialize() == pipeline_wo_named_groups.serialize()

# flake8: noqa: E501
from eventus_orchestrator_fbs.fbs.v1_instance_pipelines_config_values_response import (
    InstancePipelinesConfigValuesResponse,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    ActionAfterErroneousExecution,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    ErroneousStatisticsLevel,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import FanOut
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    FiltersDisjunction,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import Operation
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationArgArrayOfBool,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationArgArrayOfNumbers,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationArgArrayOfString,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationArgBool,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationArgNumber,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationArgString,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationArgVariadic,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationList,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationListOutputVariant,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationType,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OperationVariant,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    OutputVariant,
)
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import Sink
from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (
    SwitchOperation,
)


_OpTypeEnum = OperationType.OperationType
_OP_TYPE_MAPPING = {
    _OpTypeEnum.mapper: 'mapper',
    _OpTypeEnum.filter: 'filter',
    _OpTypeEnum: 'custom',
}


def _fbs_operation_arg_to_json(value_fbs, value_type_fbs):
    value_type_enum = OperationArgVariadic.OperationArgVariadic

    if value_type_fbs == value_type_enum.OperationArgString:
        value = OperationArgString.OperationArgString()
        value.Init(value_fbs.Bytes, value_fbs.Pos)
        return value.Value().decode('utf-8')
    if value_type_fbs == value_type_enum.OperationArgNumber:
        value = OperationArgNumber.OperationArgNumber()
        value.Init(value_fbs.Bytes, value_fbs.Pos)
        return value.Value()
    if value_type_fbs == value_type_enum.OperationArgBool:
        value = OperationArgBool.OperationArgBool()
        value.Init(value_fbs.Bytes, value_fbs.Pos)
        return value.Value()
    if value_type_fbs == value_type_enum.OperationArgArrayOfString:
        value = OperationArgArrayOfString.OperationArgArrayOfString()
        value.Init(value_fbs.Bytes, value_fbs.Pos)
        return [
            value.Value(i).decode('utf-8') for i in range(value.ValueLength())
        ]
    if value_type_fbs == value_type_enum.OperationArgArrayOfNumbers:
        value = OperationArgArrayOfNumbers.OperationArgArrayOfNumbers()
        value.Init(value_fbs.Bytes, value_fbs.Pos)
        return [value.Value(i) for i in range(value.ValueLength())]
    if value_type_fbs == value_type_enum.OperationArgArrayOfBool:
        value = OperationArgArrayOfBool.OperationArgArrayOfBool()
        value.Init(value_fbs.Bytes, value_fbs.Pos)
        return [value.Value(i) for i in range(value.ValueLength())]

    return None


def _fbs_arguments_to_json(obj):
    res = {}

    for i in range(obj.ArgumentsLength()):
        arg = obj.Arguments(i)
        name = arg.Name().decode('utf-8')
        value = arg.Value()
        value_type = arg.ValueType()

        res[name] = _fbs_operation_arg_to_json(value, value_type)

    return res


def _fbs_error_policy_to_json(obj):
    res = {}
    action_enum = ActionAfterErroneousExecution.ActionAfterErroneousExecution
    action_enum_val = obj.ErrorHandlingPolicy().ActionAfterErroneousExecution()

    level_enum = ErroneousStatisticsLevel.ErroneousStatisticsLevel
    level_enum_val = obj.ErrorHandlingPolicy().ErroneousStatisticsLevel()

    if action_enum_val is not None:
        action_str = (
            'propagate'
            if action_enum_val == action_enum.propagate
            else 'reject'
        )
        res['action_after_erroneous_execution'] = action_str

    if level_enum_val is not None:
        level_str = (
            'error' if level_enum_val == level_enum.error else 'warning'
        )
        res['erroneous_statistics_level'] = level_str

    if obj.ErrorHandlingPolicy().RetryPolicy() is not None:
        retry_policy = {}
        retry_policy['attempts'] = (
            obj.ErrorHandlingPolicy().RetryPolicy().Attempts()
        )
        retry_policy['min_delay_ms'] = (
            obj.ErrorHandlingPolicy().RetryPolicy().MinDelayMs()
        )
        retry_policy['max_delay_ms'] = (
            obj.ErrorHandlingPolicy().RetryPolicy().MaxDelayMs()
        )
        retry_policy['delay_factor'] = (
            obj.ErrorHandlingPolicy().RetryPolicy().DelayFactor()
        )

        res['retry_policy'] = retry_policy

    return res


def _fbs_source_to_json(source):
    res = {}
    res['name'] = source.Name().decode('utf-8')
    res['arguments'] = _fbs_arguments_to_json(source)
    return res


def _fbs_sink_to_json(sink):
    res = {}
    res['sink_name'] = sink.Name().decode('utf-8')
    res['arguments'] = _fbs_arguments_to_json(sink)
    if sink.ErrorHandlingPolicy() is not None:
        res['error_handling_policy'] = _fbs_error_policy_to_json(sink)
    return res


def _fbs_fanout_to_json(fanout):
    def get_value_and_type(outp):
        return outp.Output(), outp.OutputType()

    outputs = [
        _fbs_output_variant_to_json(*get_value_and_type(fanout.Outputs(i)))
        for i in range(fanout.OutputsLength())
    ]

    return {'outputs': outputs}


def _fbs_operation_to_json(oper):
    res = {}

    res['operation_name'] = oper.OperationName().decode('utf-8')
    res['type'] = _OP_TYPE_MAPPING[oper.Type()]
    res['arguments'] = _fbs_arguments_to_json(oper)

    return res


def _fbs_switch_op_item_to_json(item):
    res = {}
    res['filters'] = [
        _fbs_operation_to_json(item.Filters(i))
        for i in range(item.FiltersLength())
    ]
    res['arguments'] = _fbs_arguments_to_json(item)
    return res


def _fbs_switch_operation_to_json(switch_op):
    res = {}
    res['operation_name'] = switch_op.OperationName().decode('utf-8')
    res['type'] = _OP_TYPE_MAPPING[switch_op.Type()]
    res['options'] = [
        _fbs_switch_op_item_to_json(switch_op.Options(i))
        for i in range(switch_op.OptionsLength())
    ]
    return res


def _fbs_filters_disjunction_to_json(filt_disj):
    res = {}
    res['filters'] = [
        _fbs_operation_to_json(filt_disj.Filters(i))
        for i in range(filt_disj.FiltersLength())
    ]
    return res


def _fbs_operation_variant_to_json(op_variant, op_variant_type):
    op_variant_enum = OperationVariant.OperationVariant

    if op_variant_type == op_variant_enum.Operation:
        value = Operation.Operation()
        value.Init(op_variant.Bytes, op_variant.Pos)
        return _fbs_operation_to_json(value)
    if op_variant_type == op_variant_enum.SwitchOperation:
        value = SwitchOperation.SwitchOperation()
        value.Init(op_variant.Bytes, op_variant.Pos)
        return _fbs_switch_operation_to_json(value)
    if op_variant_type == op_variant_enum.FiltersDisjunction:
        value = FiltersDisjunction.FiltersDisjunction()
        value.Init(op_variant.Bytes, op_variant.Pos)
        return _fbs_filters_disjunction_to_json(value)

    return None


def _fbs_operation_node_to_json(op_node):
    operation_body = {}
    operation_body['name'] = op_node.Name().decode('utf-8')
    operation_body['is_disabled'] = op_node.IsDisabled()
    operation_body['operation_variant'] = _fbs_operation_variant_to_json(
        op_node.Operation(), op_node.OperationType(),
    )
    if op_node.ErrorHandlingPolicy() is not None:
        operation_body['error_handling_policy'] = _fbs_error_policy_to_json(
            op_node,
        )

    return operation_body


def _fbs_operation_list_to_json(op_list):
    res = {}
    res['output'] = _fbs_op_list_outp_var_to_json(
        op_list.Output(), op_list.OutputType(),
    )
    res['operations'] = [
        _fbs_operation_node_to_json(op_list.Operations(i))
        for i in range(op_list.OperationsLength())
    ]
    return res


def _fbs_op_list_outp_var_to_json(outp_var, outp_var_type):
    op_list_outp_var_enum = (
        OperationListOutputVariant.OperationListOutputVariant
    )

    if outp_var_type == op_list_outp_var_enum.FanOut:
        value = FanOut.FanOut()
        value.Init(outp_var.Bytes, outp_var.Pos)
        return _fbs_fanout_to_json(value)
    if outp_var_type == op_list_outp_var_enum.Sink:
        value = Sink.Sink()
        value.Init(outp_var.Bytes, outp_var.Pos)
        return _fbs_sink_to_json(value)

    return None


def _fbs_output_variant_to_json(outp_var, outp_var_type):
    outp_var_enum = OutputVariant.OutputVariant

    if outp_var_type == outp_var_enum.OperationList:
        value = OperationList.OperationList()
        value.Init(outp_var.Bytes, outp_var.Pos)
        return _fbs_operation_list_to_json(value)
    if outp_var_type == outp_var_enum.FanOut:
        value = FanOut.FanOut()
        value.Init(outp_var.Bytes, outp_var.Pos)
        return _fbs_fanout_to_json(value)
    if outp_var_type == outp_var_enum.Sink:
        value = Sink.Sink()
        value.Init(outp_var.Bytes, outp_var.Pos)
        return _fbs_sink_to_json(value)

    return None


def _fbs_pipeline_to_json(pipeline):
    res = {}
    res['name'] = pipeline.Name().decode('utf-8')
    res['is_disabled'] = pipeline.IsDisabled()
    res['source'] = _fbs_source_to_json(pipeline.Source())
    res['root'] = _fbs_output_variant_to_json(
        pipeline.Root(), pipeline.RootType(),
    )
    res['number_of_threads'] = pipeline.NumberOfThreads()
    return res


def _fbs_pipelines_vector_to_json(pipelines):
    return [_fbs_pipeline_to_json(pipeline) for pipeline in pipelines]


def fbs_instance_pipelines_to_json(
        data: InstancePipelinesConfigValuesResponse,
):
    res = {}
    res['cursor'] = data.Cursor().decode('utf-8')
    res['pipelines'] = _fbs_pipelines_vector_to_json(
        [data.Pipelines(i) for i in range(data.PipelinesLength())],
    )

    return res

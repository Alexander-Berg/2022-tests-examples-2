import flatbuffers

from eventus_orchestrator_mock import fbs_tools


def _make_schema_arguments_obj(builder, cfg, start_vector):
    arguments_obj = None
    if 'arguments' in cfg:
        arguments_list = [
            {'name': n, 'value': v} for n, v in cfg['arguments'].items()
        ]
        arguments_obj = fbs_tools.make_fbs_vector_via_func(
            builder, arguments_list, _make_schema_operation_arg, start_vector,
        )
    return arguments_obj


def _make_schema_source(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        Source,
        Operation,
    )

    name_obj = builder.CreateString(cfg['name'])

    arguments_obj = _make_schema_arguments_obj(
        builder, cfg, Source.SourceStartArgumentsVector,
    )

    Source.SourceStart(builder)
    Source.SourceAddName(builder, name_obj)
    if arguments_obj is not None:
        Source.SourceAddArguments(builder, arguments_obj)
    obj = Source.SourceEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_sink(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        Sink,
        Operation,
    )

    name_obj = builder.CreateString(cfg['sink_name'])

    error_handling_policy = None

    if 'error_handling_policy' in cfg:
        error_handling_policy = _make_schema_error_policy(
            builder, cfg['error_handling_policy'],
        )

    arguments_obj = _make_schema_arguments_obj(
        builder, cfg, Sink.SinkStartArgumentsVector,
    )

    Sink.SinkStart(builder)
    Sink.SinkAddName(builder, name_obj)
    if arguments_obj is not None:
        Sink.SinkAddArguments(builder, arguments_obj)
    if error_handling_policy is not None:
        Sink.SinkAddErrorHandlingPolicy(builder, error_handling_policy)
    obj = Sink.SinkEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_operation_arg(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        OperationArg,
        OperationArgVariadic,
        #
        OperationArgString,
        OperationArgNumber,
        OperationArgBool,
        OperationArgArrayOfString,
        OperationArgArrayOfNumbers,
        OperationArgArrayOfBool,
    )
    _value_type = OperationArgVariadic.OperationArgVariadic

    name_obj = None
    if 'name' in cfg:
        name_obj = builder.CreateString(cfg['name'])

    value_type_obj = None
    value_obj = None
    if isinstance(cfg['value'], str):
        value_type_obj = _value_type.OperationArgString
        _value_obj = builder.CreateString(cfg['value'])
        OperationArgString.OperationArgStringStart(builder)
        OperationArgString.OperationArgStringAddValue(builder, _value_obj)
        value_obj = OperationArgString.OperationArgStringEnd(builder)
        builder.Finish(value_obj)

    elif isinstance(cfg['value'], bool):
        value_type_obj = _value_type.OperationArgBool
        OperationArgBool.OperationArgBoolStart(builder)
        OperationArgBool.OperationArgBoolAddValue(builder, cfg['value'])
        value_obj = OperationArgBool.OperationArgBoolEnd(builder)
        builder.Finish(value_obj)

    elif isinstance(cfg['value'], (float, int)):
        value_type_obj = _value_type.OperationArgNumber
        OperationArgNumber.OperationArgNumberStart(builder)
        OperationArgNumber.OperationArgNumberAddValue(builder, cfg['value'])
        value_obj = OperationArgNumber.OperationArgNumberEnd(builder)
        builder.Finish(value_obj)

    elif isinstance(cfg['value'], list):
        if len(cfg['value']) == sum(
                [isinstance(v, str) for v in cfg['value']],
        ):
            _val_kind = OperationArgArrayOfString
            value_type_obj = _value_type.OperationArgArrayOfString
            _value_obj = fbs_tools.make_fbs_vector_via_func(
                builder,
                cfg['value'],
                fbs_tools.make_fbs_string,
                _val_kind.OperationArgArrayOfStringStartValueVector,
            )
            _val_kind.OperationArgArrayOfStringStart(builder)
            _val_kind.OperationArgArrayOfStringAddValue(builder, _value_obj)
            value_obj = _val_kind.OperationArgArrayOfStringEnd(builder)
            builder.Finish(value_obj)

        elif len(cfg['value']) == sum(
            [isinstance(v, bool) for v in cfg['value']],
        ):
            _val_kind = OperationArgArrayOfBool
            value_type_obj = _value_type.OperationArgArrayOfBool
            _value_obj = fbs_tools.make_fbs_vector_via_func(
                builder,
                cfg['value'],
                lambda _, b: b,
                _val_kind.OperationArgArrayOfBoolStartValueVector,
                builder.PrependBool,
            )

            _val_kind.OperationArgArrayOfBoolStart(builder)
            _val_kind.OperationArgArrayOfBoolAddValue(builder, _value_obj)
            value_obj = _val_kind.OperationArgArrayOfBoolEnd(builder)
            builder.Finish(value_obj)

        elif len(cfg['value']) == sum(
            [isinstance(v, (float, int)) for v in cfg['value']],
        ):
            _val_kind = OperationArgArrayOfNumbers
            value_type_obj = _value_type.OperationArgArrayOfNumbers
            _value_obj = fbs_tools.make_fbs_vector_via_func(
                builder,
                cfg['value'],
                lambda _, n: float(n),
                _val_kind.OperationArgArrayOfNumbersStartValueVector,
                builder.PrependFloat64,
            )

            _val_kind.OperationArgArrayOfNumbersStart(builder)
            _val_kind.OperationArgArrayOfNumbersAddValue(builder, _value_obj)
            value_obj = _val_kind.OperationArgArrayOfNumbersEnd(builder)
            builder.Finish(value_obj)
        else:
            raise Exception(
                'OperationArg value contains array of mixed '
                'type or different from float or string',
            )
    else:
        raise Exception('OperationArg value contains unsupported type')

    OperationArg.OperationArgStart(builder)
    if name_obj is not None:
        OperationArg.OperationArgAddName(builder, name_obj)
    OperationArg.OperationArgAddValueType(builder, value_type_obj)
    OperationArg.OperationArgAddValue(builder, value_obj)
    obj = OperationArg.OperationArgEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_operation_type(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        OperationType,
    )
    mapped_types = {
        'filter': OperationType.OperationType.filter,
        'mapper': OperationType.OperationType.mapper,
        'custom': OperationType.OperationType.custom,
    }
    if cfg not in mapped_types:
        raise Exception('Unknown OperationType value: {}'.format(cfg))
    return mapped_types[cfg]


def _make_schema_operation(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        Operation,
    )

    arguments_obj = _make_schema_arguments_obj(
        builder, cfg, Operation.OperationStartArgumentsVector,
    )

    operation_name_obj = builder.CreateString(cfg['operation_name'])
    type_obj = _make_schema_operation_type(builder, cfg['type'])

    Operation.OperationStart(builder)
    Operation.OperationAddOperationName(builder, operation_name_obj)
    Operation.OperationAddType(builder, type_obj)
    if arguments_obj is not None:
        Operation.OperationAddArguments(builder, arguments_obj)
    obj = Operation.OperationEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_switch_operation_item(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        SwitchOperationItem,
    )

    filters_obj = fbs_tools.make_fbs_vector_via_func(
        builder,
        cfg['filters'],
        _make_schema_operation,
        SwitchOperationItem.SwitchOperationItemStartFiltersVector,
    )
    arguments_obj = _make_schema_arguments_obj(
        builder,
        cfg,
        SwitchOperationItem.SwitchOperationItemStartArgumentsVector,
    )

    SwitchOperationItem.SwitchOperationItemStart(builder)
    SwitchOperationItem.SwitchOperationItemAddFilters(builder, filters_obj)
    if arguments_obj is not None:
        SwitchOperationItem.SwitchOperationItemAddArguments(
            builder, arguments_obj,
        )
    obj = SwitchOperationItem.SwitchOperationItemEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_switch_operation(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        SwitchOperation,
    )

    operation_name_obj = builder.CreateString(cfg['operation_name'])
    type_obj = _make_schema_operation_type(builder, cfg['type'])
    options_obj = fbs_tools.make_fbs_vector_via_func(
        builder,
        cfg['options'],
        _make_schema_switch_operation_item,
        SwitchOperation.SwitchOperationStartOptionsVector,
    )

    SwitchOperation.SwitchOperationStart(builder)
    SwitchOperation.SwitchOperationAddOperationName(
        builder, operation_name_obj,
    )
    SwitchOperation.SwitchOperationAddType(builder, type_obj)
    SwitchOperation.SwitchOperationAddOptions(builder, options_obj)
    obj = SwitchOperation.SwitchOperationEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_filters_disjunction(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        FiltersDisjunction,
    )

    filters_obj = fbs_tools.make_fbs_vector_via_func(
        builder,
        cfg['filters'],
        _make_schema_operation,
        FiltersDisjunction.FiltersDisjunctionStartFiltersVector,
    )

    FiltersDisjunction.FiltersDisjunctionStart(builder)
    FiltersDisjunction.FiltersDisjunctionAddFilters(builder, filters_obj)
    obj = FiltersDisjunction.FiltersDisjunctionEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_operation_variant(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        OperationVariant,
    )

    operation_obj = None
    switch_operation_obj = None
    filters_disjunction_obj = None

    if 'options' in cfg:
        switch_operation_obj = _make_schema_switch_operation(builder, cfg)
    elif 'filters' in cfg:
        filters_disjunction_obj = _make_schema_filters_disjunction(
            builder, cfg,
        )
    else:
        operation_obj = _make_schema_operation(builder, cfg)

    if operation_obj is not None:
        return operation_obj, OperationVariant.OperationVariant().Operation
    if switch_operation_obj is not None:
        return (
            switch_operation_obj,
            OperationVariant.OperationVariant().SwitchOperation,
        )
    if filters_disjunction_obj is not None:
        return (
            filters_disjunction_obj,
            OperationVariant.OperationVariant().FiltersDisjunction,
        )

    return None, None


def _make_schema_retry_policy(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        RetryPolicy,
    )

    RetryPolicy.RetryPolicyStart(builder)
    if 'attempts' in cfg:
        RetryPolicy.RetryPolicyAddAttempts(builder, cfg['attempts'])

    if 'min_delay_ms' in cfg:
        RetryPolicy.RetryPolicyAddMinDelayMs(builder, cfg['min_delay_ms'])

    if 'max_delay_ms' in cfg:
        RetryPolicy.RetryPolicyAddMaxDelayMs(builder, cfg['max_delay_ms'])

    if 'delay_factor' in cfg:
        RetryPolicy.RetryPolicyAddDelayFactor(builder, cfg['delay_factor'])

    obj = RetryPolicy.RetryPolicyEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_action_after_error(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        ActionAfterErroneousExecution,
    )

    action = ActionAfterErroneousExecution.ActionAfterErroneousExecution

    mapped_types = {
        'propagate': (action.propagate),
        'reject': (
            ActionAfterErroneousExecution.ActionAfterErroneousExecution.reject
        ),
    }
    if cfg not in mapped_types:
        raise Exception(
            'Unknown ActionAfterErroneousExecution value: {}'.format(cfg),
        )
    return mapped_types[cfg]


def _make_schema_erroneous_statistics_level(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        ErroneousStatisticsLevel,
    )

    level = ErroneousStatisticsLevel.ErroneousStatisticsLevel

    mapped_types = {'error': (level.error), 'warning': (level.warning)}
    if cfg not in mapped_types:
        raise Exception(
            'Unknown ErroneousStatisticsLevel value: {}'.format(cfg),
        )
    return mapped_types[cfg]


def _make_schema_error_policy(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        ErrorHandlingPolicy,
    )

    retry_policy = None
    if 'retry_policy' in cfg:
        retry_policy = _make_schema_retry_policy(builder, cfg['retry_policy'])

    action_after_error = None
    if 'action_after_erroneous_execution' in cfg:
        action_after_error = _make_schema_action_after_error(
            builder, cfg['action_after_erroneous_execution'],
        )

    statistic_level = None
    if 'erroneous_statistics_level' in cfg:
        statistic_level = _make_schema_erroneous_statistics_level(
            builder, cfg['erroneous_statistics_level'],
        )

    ErrorHandlingPolicy.ErrorHandlingPolicyStart(builder)

    if retry_policy is not None:
        ErrorHandlingPolicy.ErrorHandlingPolicyAddRetryPolicy(
            builder, retry_policy,
        )

    ehp = ErrorHandlingPolicy
    add_action = ehp.ErrorHandlingPolicyAddActionAfterErroneousExecution
    add_level = ehp.ErrorHandlingPolicyAddErroneousStatisticsLevel

    if action_after_error is not None:
        add_action(builder, action_after_error)

    if statistic_level is not None:
        add_level(builder, statistic_level)

    obj = ErrorHandlingPolicy.ErrorHandlingPolicyEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_operation_node(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        OperationNode,
    )

    name_obj = builder.CreateString(cfg['name'])

    is_disabled_obj = None
    if 'is_disabled' in cfg:
        is_disabled_obj = cfg['is_disabled']
    operation_obj, operation_type = None, None
    if 'operation_variant' in cfg:
        operation_obj, operation_type = _make_schema_operation_variant(
            builder, cfg['operation_variant'],
        )
    error_handling_policy = None

    if 'error_handling_policy' in cfg:
        error_handling_policy = _make_schema_error_policy(
            builder, cfg['error_handling_policy'],
        )

    OperationNode.OperationNodeStart(builder)
    OperationNode.OperationNodeAddName(builder, name_obj)
    if is_disabled_obj is not None:
        OperationNode.OperationNodeAddIsDisabled(builder, is_disabled_obj)
    if operation_obj is not None:
        OperationNode.OperationNodeAddOperationType(builder, operation_type)
        OperationNode.OperationNodeAddOperation(builder, operation_obj)
    if error_handling_policy is not None:
        OperationNode.OperationNodeAddErrorHandlingPolicy(
            builder, error_handling_policy,
        )
    obj = OperationNode.OperationNodeEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_fanout_output(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        FanoutOutputWrapper,
    )

    output_obj, output_type = _make_schema_output_variant(builder, cfg)

    FanoutOutputWrapper.FanoutOutputWrapperStart(builder)
    FanoutOutputWrapper.FanoutOutputWrapperAddOutputType(builder, output_type)
    FanoutOutputWrapper.FanoutOutputWrapperAddOutput(builder, output_obj)
    obj = FanoutOutputWrapper.FanoutOutputWrapperEnd(builder)
    builder.Finish(obj)

    return obj


def _make_schema_fanout(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        FanOut,
    )

    if not isinstance(cfg, dict):
        raise Exception(
            'FanOut expects to be a dict, but contains "{}"'.format(cfg),
        )

    if not isinstance(cfg['outputs'], list):
        raise Exception(
            'FanOut.outputs expects to be a list, but contains "{}"'.format(
                cfg['outputs'],
            ),
        )

    outputs_obj = fbs_tools.make_fbs_vector_via_func(
        builder,
        cfg['outputs'],
        _make_schema_fanout_output,
        FanOut.FanOutStartOutputsVector,
    )

    FanOut.FanOutStart(builder)
    FanOut.FanOutAddOutputs(builder, outputs_obj)
    obj = FanOut.FanOutEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_op_list_output_variant(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        OperationListOutputVariant,
    )
    fanout_obj = None
    sink_obj = None

    if 'outputs' in cfg:
        fanout_obj = _make_schema_fanout(builder, cfg)
    if 'sink_name' in cfg:
        sink_obj = _make_schema_sink(builder, cfg)

    if fanout_obj is not None:
        return (
            fanout_obj,
            OperationListOutputVariant.OperationListOutputVariant().FanOut,
        )
    if sink_obj is not None:
        return (
            sink_obj,
            OperationListOutputVariant.OperationListOutputVariant().Sink,
        )

    return None, None


def _make_schema_operation_list(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        OperationList,
    )
    operations_obj = fbs_tools.make_fbs_vector_via_func(
        builder,
        cfg['operations'],
        _make_schema_operation_node,
        OperationList.OperationListStartOperationsVector,
    )
    output_obj, output_type = _make_schema_op_list_output_variant(
        builder, cfg['output'],
    )

    OperationList.OperationListStart(builder)
    OperationList.OperationListAddOperations(builder, operations_obj)
    OperationList.OperationListAddOutputType(builder, output_type)
    OperationList.OperationListAddOutput(builder, output_obj)

    obj = OperationList.OperationListEnd(builder)
    builder.Finish(obj)
    return obj


def _make_schema_output_variant(builder, cfg):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        OutputVariant,
    )
    operation_list_obj = None
    fanout_obj = None
    sink_obj = None

    if 'operations' in cfg:
        operation_list_obj = _make_schema_operation_list(builder, cfg)
    if 'outputs' in cfg:
        fanout_obj = _make_schema_fanout(builder, cfg)
    if 'sink_name' in cfg:
        sink_obj = _make_schema_sink(builder, cfg)

    if operation_list_obj is not None:
        return operation_list_obj, OutputVariant.OutputVariant().OperationList
    if fanout_obj is not None:
        return fanout_obj, OutputVariant.OutputVariant().FanOut
    if sink_obj is not None:
        return sink_obj, OutputVariant.OutputVariant().Sink

    return None, None


def _make_schema_pipeline(builder, pipeline):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_pipelines_config_schema import (  # noqa: IS001
        Pipeline,
    )

    name_obj = builder.CreateString(pipeline['name'])
    is_disabled_obj = None
    if 'is_disabled' in pipeline:
        is_disabled_obj = pipeline['is_disabled']
    source_obj = _make_schema_source(builder, pipeline['source'])
    root_obj, root_type = _make_schema_output_variant(
        builder, pipeline['root'],
    )

    Pipeline.PipelineStart(builder)
    Pipeline.PipelineAddName(builder, name_obj)
    if is_disabled_obj is not None:
        Pipeline.PipelineAddIsDisabled(builder, is_disabled_obj)
    if 'number_of_threads' in pipeline:
        Pipeline.PipelineAddNumberOfThreads(
            builder, pipeline['number_of_threads'],
        )
    Pipeline.PipelineAddSource(builder, source_obj)
    Pipeline.PipelineAddRootType(builder, root_type)
    Pipeline.PipelineAddRoot(builder, root_obj)

    obj = Pipeline.PipelineEnd(builder)
    builder.Finish(obj)
    return obj


def make_pipelines_config_response(pipelines_config):
    # pylint: disable=import-error
    from eventus_orchestrator_fbs.fbs.v1_instance_pipelines_config_values_response import (  # noqa: IS001
        InstancePipelinesConfigValuesResponse,
    )
    response = InstancePipelinesConfigValuesResponse
    builder = flatbuffers.Builder(0)

    cursor_obj = builder.CreateString(pipelines_config['cursor'])

    pipelines_obj = fbs_tools.make_fbs_vector_via_func(
        builder,
        pipelines_config['pipelines'],
        _make_schema_pipeline,
        response.InstancePipelinesConfigValuesResponseStartPipelinesVector,
    )

    response.InstancePipelinesConfigValuesResponseStart(builder)
    response.InstancePipelinesConfigValuesResponseAddCursor(
        builder, cursor_obj,
    )
    response.InstancePipelinesConfigValuesResponseAddPipelines(
        builder, pipelines_obj,
    )
    obj = response.InstancePipelinesConfigValuesResponseEnd(builder)
    builder.Finish(obj)
    return bytes(builder.Output())

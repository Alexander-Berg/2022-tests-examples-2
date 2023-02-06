def remove_deprecated_fields(pipeline_doc):
    # Copied from pipelines_common.Helper.serialize
    def _process(stage_or_stages):
        if isinstance(stage_or_stages, list):
            for inner in stage_or_stages:
                _process(inner.get('stages', inner))
            return

        for condition in stage_or_stages.get('conditions', []):
            if 'type' in condition:
                del condition['type']

        bindings = list(stage_or_stages.get('in_bindings', []))
        bindings += stage_or_stages.get('out_bindings', [])
        for binding in bindings:
            if 'optional' in binding:
                del binding['optional']

    _process(pipeline_doc['stages'])

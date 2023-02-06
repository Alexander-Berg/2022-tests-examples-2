import typing as tp


def sort_data(data: dict):
    def sort(data, field_name, key_name):
        data[field_name] = sorted(data[field_name], key=lambda x: x[key_name])

    sort(data, 'classes', 'name')
    sort(data, 'experiments', 'experiment_name')

    for experiment in data.get('experiments', []):
        sort(experiment, 'classes', 'name')


def convert_class_info(old_class_info, base):
    def to_pricing_coeffs(obj):
        coeffs = {'value': obj['value']}
        if 'surcharge' in obj:
            coeffs['surcharge'] = {
                'value': obj['surcharge'],
                'alpha': obj['surcharge_alpha'],
                'beta': obj['surcharge_beta'],
            }
        return coeffs

    new_class_info = base.copy() if base else {}
    new_class_info.update(
        {
            'name': old_class_info['name'],
            'surge': to_pricing_coeffs(old_class_info),
            'value_raw': old_class_info['value_raw'],
        },
    )

    if 'explicit_antisurge' in old_class_info:
        new_class_info['explicit_antisurge'] = to_pricing_coeffs(
            old_class_info['explicit_antisurge'],
        )

    if 'value_smooth' in old_class_info:
        new_class_info.setdefault('calculation_meta', {}).setdefault(
            'smooth', {},
        )['point_a'] = (
            {
                'value': old_class_info['value_smooth'],
                'is_default': old_class_info['value_smooth_is_default'],
            }
        )

    if 'value_smooth_b' in old_class_info:
        new_class_info.setdefault('calculation_meta', {}).setdefault(
            'smooth', {},
        )['point_b'] = (
            {
                'value': old_class_info['value_smooth_b'],
                'is_default': old_class_info['value_smooth_b_is_default'],
            }
        )

    for field in [
            'reason',
            'f_derivative',
            'ps',
            'pins_meta',
            'deviation_from_target_abs',
            'ps_shift_past_raw',
    ]:
        if field in old_class_info:
            new_class_info.setdefault('calculation_meta', {})[
                field
            ] = old_class_info[field]

    for field in ['pins', 'free', 'free_chain', 'radius', 'total']:
        if field in old_class_info:
            new_class_info.setdefault('calculation_meta', {}).setdefault(
                'counts', {},
            )[field] = old_class_info[field]

    return new_class_info


def convert_response(response: dict, base: dict, class_info_base: dict = None):
    def convert_class_info_with_base(class_info):
        return convert_class_info(class_info, class_info_base)

    new_response = {
        'zone_id': response['zone_id'],
        'user_layer': base.get('user_layer', 'default'),
        'experiment_id': base['experiment_id'],
        'experiment_name': base.get('experiment_name', 'default'),
        'experiment_layer': base.get('experiment_layer', 'default'),
        'is_cached': base.get('is_cached', False),
        'classes': list(
            map(convert_class_info_with_base, response['classes']),
        ),
        'experiments': [],
        'experiment_errors': base.get('experiment_errors', []),
    }

    return new_response


def get_stage_logs(yt_logs: list) -> tp.Dict[str, tp.Dict[str, list]]:
    # {calculation_id: {stage_name: [<logs>]}}
    stage_logs: dict = {}
    for yt_log in yt_logs:
        calculation_stage_logs = stage_logs[yt_log['calculation_id']] = {}
        for meta in yt_log['calculation']['$meta']:
            calculation_stage_logs.setdefault(meta['$stage'], []).extend(
                meta['$logs'],
            )

    return stage_logs


def get_full_calculation_meta(yt_logs: list) -> dict:
    def is_leaf(yt_log):
        return '$history' in yt_log

    def get_last_value(history_leaf):
        return history_leaf['$history'][-1]['$value']

    def get_final_state_from_yt_logs(yt_log):
        def process_list(yt_log_node: list):
            return list(map(get_final_state_from_yt_logs, yt_log_node))

        def process_dict(yt_log_node: dict):
            out = {}
            for key, value in yt_log_node.items():
                out[key] = get_final_state_from_yt_logs(value)
            return out

        def process_node(yt_log_node):
            node_handlers = {list: process_list, dict: process_dict}
            return node_handlers[type(yt_log_node)](yt_log_node)

        if is_leaf(yt_log):
            return get_last_value(yt_log)

        return process_node(yt_log)

    # {calculation_id: {class_name: {<full_calculation_meta>}}}
    full_meta: dict = {}
    for yt_log in yt_logs:
        calculation_full_meta = full_meta[yt_log['calculation_id']] = {}
        calculation = yt_log['calculation']
        if 'classes' in calculation:
            for class_name, class_info in calculation['classes'].items():
                calculation_full_meta[class_name] = (
                    get_final_state_from_yt_logs(
                        class_info.get('calculation_meta', {}),
                    )
                )
        else:
            # native fallback
            for class_info in calculation['response']['classes']:
                calculation_full_meta[class_info['name']] = class_info.get(
                    'calculation_meta', {},
                )

    return full_meta


class JsonOverrideOverwrite:
    """
    if override wrapped in this type, json_override will not go into existing
    value and instead will just overwrite it
    """

    def __init__(self, value):
        self.value = value


class JsonOverrideDelete:
    """
    if override wrapped in this type, json_override will not go into existing
    value and instead will just delete it
    """

    def __init__(self):
        pass


def json_override(base, override):
    assert not isinstance(override, JsonOverrideDelete)

    if override is None:
        result = base
    elif isinstance(override, JsonOverrideOverwrite):
        result = override.value
    elif isinstance(override, dict):
        result = base if isinstance(base, dict) else {}
        for key, value in override.items():
            if key in result:
                if isinstance(value, JsonOverrideDelete):
                    del result[key]
                else:
                    result[key] = json_override(result[key], value)
            elif not isinstance(value, JsonOverrideDelete):
                result[key] = value
    elif isinstance(override, list):
        result = base if isinstance(base, list) else []
        for index, value in enumerate(override):
            if isinstance(value, JsonOverrideDelete):
                continue
            if index < len(result):
                result[index] = json_override(result[index], value)
            else:
                assert index == len(result)
                result.append(value)
        for index, value in enumerate(override):
            if isinstance(value, JsonOverrideDelete):
                del result[index]
    else:
        result = override

    return result


def sort_list_by_list(_to_sort: list, sorted_by: list) -> list:
    result = []
    to_sort = _to_sort.copy()

    for i in sorted_by:
        if i in to_sort:
            result.append(i)
            to_sort.remove(i)

    result.extend(to_sort)

    return result


def unescape_yt_logs(json):
    for calculation in json:
        for meta in calculation['calculation']['$meta']:
            for log in meta['$logs']:
                log['$timestamp'] = log['$$timestamp']
                del log['$$timestamp']

    return json

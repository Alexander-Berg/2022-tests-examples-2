def check_metrics(metrics, expectations):
    for key, value in metrics.items():
        if key in expectations.keys():
            assert expectations[key] == value, (
                key
                + ' = '
                + str(value)
                + ' (but expected: '
                + str(expectations[key])
                + ')'
            )
        else:
            assert value == 0, key + ' = ' + str(value)
    for key in expectations.keys():
        if key not in metrics.keys():
            assert False, 'metrics has no "' + key + '" key'


def has_metrics(metrics, expectations):
    for key, value in expectations.items():
        if key not in metrics.keys() and value != 0:
            assert False, 'metrics has no "' + key + '" key'
        assert value == metrics[key], (
            key + ' = ' + metrics[key] + ' (but expected: ' + str(value) + ')'
        )


def remove_key(json, keys):
    current = json
    for k in keys[:-1]:
        current = current[k]

    del current[keys[-1]]


def is_subjson(subjson, json, message='<root>'):
    if isinstance(subjson, dict):
        for key, value in subjson.items():
            assert key in json, 'key ' + message + '/' + key + ' not found'
            is_subjson(value, json[key], message + '/' + key)
    elif isinstance(subjson, list):
        assert False, 'please, implement this path'
    else:
        assert subjson == json, (
            'assertion failed for key '
            + message
            + ': expected '
            + str(subjson)
            + ' but has '
            + str(json)
        )

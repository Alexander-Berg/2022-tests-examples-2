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


def cskv_to_set(value):
    return set(x.strip() for x in value.split(','))


def assert_cskvs_are_equal(value, expected, message=''):
    assert cskv_to_set(value) == cskv_to_set(expected), message

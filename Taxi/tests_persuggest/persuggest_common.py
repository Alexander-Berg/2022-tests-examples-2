import json

# Parse stringified json fields to avoid problems with
# keys order inside objects
def jsonify(obj):
    for result in obj['results']:
        if 'log' not in result:
            continue
        if isinstance(result['log'], dict):
            if 'tags' in result['log']:
                result['log']['tags'].sort()
            continue
        if not result['log'].startswith('{'):
            continue
        result['log'] = json.loads(result['log'])
        if 'tags' in result['log']:
            result['log']['tags'].sort()
    return obj


def add_data_to_log(message, data_dict):
    log_key = next(k for k in ('log', 'prev_log') if k in message)
    log = message[log_key]
    if not isinstance(log, dict) and log.startswith('{'):
        log = log.strip()
        log = json.loads(log)
    elif not isinstance(log, dict):
        log = {'uri': log.strip()}
    log.update(data_dict)
    message[log_key] = json.dumps(log)


def logparse(data):
    if 'results' not in data:
        return data
    for result in data['results']:
        if 'log' not in result:
            continue
        if isinstance(result['log'], dict):
            if 'tags' in result['log']:
                result['log']['tags'].sort()
            continue
        if not result['log'].startswith('{'):
            continue
        result['log'] = json.loads(result['log'])
        if 'tags' in result['log']:
            result['log']['tags'].sort()
    return data


def compare_responses(*, actual, expected, request=None, mode=None):
    if (mode or '') == '':
        if request is not None:
            mode = request['state']['current_mode']
    if not isinstance(actual, dict):
        assert actual.status_code == 200
        actual = actual.json()
    if mode != 'grocery':
        # ignore building-id for non-grocery requests
        for result in expected.get('results', []):
            if 'building_id' in result:
                del result['building_id']
    logparse(actual)
    logparse(expected)
    assert actual == expected

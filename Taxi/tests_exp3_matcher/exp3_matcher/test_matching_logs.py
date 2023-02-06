import ast
import json

import pytest


class Exp3LoggerController:
    def __init__(self, file_path):
        self.file_path = file_path
        self.nlines_before_test = sum(1 for line in open(self.file_path))

    def get_this_test_match_logs(self):
        res = []
        with self.file_path.open('r') as file:
            for i, line in enumerate(file):
                if i >= self.nlines_before_test:
                    res.append(line)
        return res


@pytest.fixture(name='exp3_logger')
def _exp3_logger(testsuite_build_dir):
    return Exp3LoggerController(testsuite_build_dir / 'exp3-matched.log')


def parse_tskv_log(log_str):
    parts = log_str.replace('\\\\', '\\').split('\t')
    assert parts[0] == 'tskv'
    log_dict = {}
    for part in parts[1:]:
        key, value = part.split('=', 1)
        log_dict[key] = value.strip()
    return log_dict


@pytest.mark.experiments3(
    name='test_logs',
    consumers=['launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[],
    default_value={'key': 228},
)
@pytest.mark.experiments3(
    name='signal_clause',
    consumers=['launch'],
    clauses=[
        {
            'is_signal': True,
            'predicate': {'type': 'true'},
            'value': {'key': 'clause_value'},
        },
    ],
)
async def test_matching_logs(taxi_exp3_matcher, exp3_logger):

    request = {
        'consumer': 'launch',
        'args': [
            {'name': 'some_kwarg', 'type': 'string', 'value': 'some_value'},
            {'name': 'bool_kwarg', 'type': 'bool', 'value': False},
            {'name': 'int_kwarg', 'type': 'int', 'value': 228},
            {
                'name': 'application_kwarg',
                'type': 'application',
                'value': 'some_value',
            },
            {'name': 'double_kwarg', 'type': 'double', 'value': 228.288},
            {
                'name': 'av_kwarg',
                'type': 'application_version',
                'value': '1.1.1',
            },
            {'name': 'si_kwarg', 'type': 'set_int', 'value': [1, 2, 3]},
            {
                'name': 'ss_kwarg',
                'type': 'set_string',
                'value': ['1', '2', '3'],
            },
            {'name': 'point_kwarg', 'type': 'point', 'value': [1.1, 2.2]},
        ],
    }
    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value']['key'] == 228

    logs = exp3_logger.get_this_test_match_logs()
    assert len(logs) == 1

    log = parse_tskv_log(logs[0])

    assert log['experiment3_type'] == 'experiment'
    assert log['consumer'] == 'launch'

    kwargs = json.loads(log['kwargs'])
    assert kwargs['some_kwarg'] == 'some_value'
    assert kwargs['consumer'] == 'launch'
    assert kwargs['is_prestable'] in {'0', '1'}

    assert kwargs['application_kwarg'] == 'some_value'
    assert kwargs['av_kwarg'] == '1.1.1'

    # facepalm...
    assert kwargs['bool_kwarg'] == '0'
    assert kwargs['int_kwarg'] == '228'
    assert kwargs['double_kwarg'] == '228.288000'
    assert kwargs['point_kwarg'] == '1.1,2.2'
    assert set(ast.literal_eval(kwargs['si_kwarg'])) == {1, 2, 3}
    assert set(ast.literal_eval(kwargs['ss_kwarg'])) == {'1', '2', '3'}

    matched = json.loads(log['matched'])
    assert len(matched) == 2
    sorted(matched, key=lambda match: match['experiment3_name'])

    assert matched[0]['position'] == 0
    assert matched[0]['is_signal'] is True
    assert matched[0]['experiment3_name'] == 'signal_clause'
    assert matched[0]['version'] == 1
    assert 'alias' not in matched[0]
    assert 'biz_revision' not in matched[0]

    assert matched[1]['position'] == -1
    assert matched[1]['is_signal'] is False
    assert matched[1]['alias'] == 'default'
    assert matched[1]['experiment3_name'] == 'test_logs'
    assert matched[1]['version'] == 2
    assert 'biz_revision' not in matched[1]


@pytest.mark.parametrize('no_logs', [True, False])
@pytest.mark.experiments3(filename='no_match_logs_experiments.json')
async def test_skip_logs_for_merged_exps_with_no_match_log_tag(
        taxi_exp3_matcher, experiments3, exp3_logger, no_logs,
):
    exps = experiments3.get_experiments('launch', 0)
    if no_logs:
        result_exps = []
        for exp in exps:
            exp['trait_tags'] = ['no-match-log']
            result_exps.append(exp)
        experiments3.add_experiments_json({'experiments': result_exps})

    request = {'consumer': 'launch', 'args': []}
    response = await taxi_exp3_matcher.post('/v1/experiments/', request)
    assert response.status_code == 200

    logs = exp3_logger.get_this_test_match_logs()
    if no_logs:
        assert logs == []
    else:
        assert len(logs) == 1
        log = parse_tskv_log(logs[0])
        assert log['experiment3_type'] == 'experiment'
        assert log['consumer'] == 'launch'

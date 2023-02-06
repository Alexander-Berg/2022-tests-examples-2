# Just copied from exp3-matcher

import pytest


@pytest.mark.experiments3(
    name='test',
    consumers=['launch'],
    match={
        'predicate': {
            'init': {
                'arg_name': 'some_arg',
                'file': 'file_228',
                'set_elem_type': 'string',
            },
            'type': 'in_file',
        },
        'enabled': True,
    },
    clauses=[],
    default_value={'key': 42},
)
def test_in_file_predicate(taxi_experiments3, mockserver):
    @mockserver.handler('/experiments3-upstream/v1/files/')
    def _mock_exp(request):
        assert request.args['id'] == 'file_228'
        return mockserver.make_response('abacaba\nqqq\nrrr\n')

    request = {
        'consumer': 'launch',
        'args': [{'name': 'some_arg', 'value': 'abacaba', 'type': 'string'}],
    }
    response = taxi_experiments3.post('/v1/experiments', request)
    assert response.status_code == 200
    assert response.json()['items'][0]['value']['key'] == 42

    # file_dump = (
    #     testsuite_build_dir / 'cache' /
    #     'exp3' / '___files' / 'file_228.string'
    # )
    # with open(file_dump) as file:
    #     assert set(file.read().split()) == {'abacaba', 'qqq', 'rrr'}


@pytest.mark.experiments3(
    name='disabled_clause_exp',
    consumers=['launch'],
    match={'predicate': {'type': 'true'}, 'enabled': True},
    clauses=[
        {
            'enabled': False,
            'predicate': {'type': 'true'},
            'value': 'value_disabled_clause',
        },
        {
            'enabled': True,
            'predicate': {'type': 'true'},
            'value': 'value_enabled_clause',
        },
    ],
)
def test_disabled_clause(taxi_experiments3):
    request = {'consumer': 'launch', 'args': []}
    response = taxi_experiments3.post('/v1/experiments', request)
    assert response.status_code == 200
    content = response.json()
    assert len(content['items']) == 1
    assert content['items'][0]['value'] == 'value_enabled_clause'

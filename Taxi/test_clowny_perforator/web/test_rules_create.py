import dataclasses
import re

import pytest


@dataclasses.dataclass
class RequestRule:
    source: str
    destination: str


@dataclasses.dataclass
class ExpectedRule:
    source: str
    destination: str
    env_type: str


@pytest.mark.parametrize(
    'request_rules, env_types, expected, expected_added',
    [
        (
            [
                RequestRule('existed_tvm_service', 'existed_tvm_service'),
                RequestRule('existed_tvm_service', 'existed_tvm_service_2'),
                RequestRule('existed_tvm_service_2', 'existed_tvm_service_2'),
            ],
            ['testing', 'production'],
            [
                ExpectedRule(
                    'existed_tvm_service', 'existed_tvm_service', 'testing',
                ),
                ExpectedRule(
                    'existed_tvm_service',
                    'existed_tvm_service_2',
                    'production',
                ),
                ExpectedRule(
                    'existed_tvm_service_2',
                    'existed_tvm_service_2',
                    'production',
                ),
                ExpectedRule(
                    'existed_tvm_service_2',
                    'existed_tvm_service_2',
                    'testing',
                ),
            ],
            [
                ExpectedRule(
                    'existed_tvm_service_2',
                    'existed_tvm_service_2',
                    'testing',
                ),
                ExpectedRule(
                    'existed_tvm_service', 'existed_tvm_service', 'production',
                ),
                ExpectedRule(
                    'existed_tvm_service',
                    'existed_tvm_service_2',
                    'production',
                ),
                ExpectedRule(
                    'existed_tvm_service_2',
                    'existed_tvm_service_2',
                    'production',
                ),
            ],
        ),
        (
            [
                RequestRule('existed_tvm_service', 'existed_tvm_service'),
                RequestRule('existed_tvm_service', 'existed_tvm_service_2'),
            ],
            None,
            [
                ExpectedRule(
                    'existed_tvm_service', 'existed_tvm_service', 'testing',
                ),
                ExpectedRule(
                    'existed_tvm_service',
                    'existed_tvm_service_2',
                    'production',
                ),
            ],
            [
                ExpectedRule(
                    'existed_tvm_service', 'existed_tvm_service', 'production',
                ),
                ExpectedRule(
                    'existed_tvm_service',
                    'existed_tvm_service_2',
                    'production',
                ),
            ],
        ),
    ],
)
@pytest.mark.pgsql('clowny_perforator', files=['service_data.sql'])
async def test_rules_create(
        web_app_client,
        cte_configs_mockserver,
        request_rules,
        env_types,
        expected,
        expected_added,
        get_tvm_rules,
):
    configs_mock = cte_configs_mockserver()
    body = _make_body(request_rules, env_types)
    handler_name = '/v1.0/internal/services/rules/create'
    response = await web_app_client.post(handler_name, json=body)
    content = await response.json()
    _assert_mock(configs_mock, get_tvm_rules, env_types, expected_added)
    cache_rules = {
        (rule.source, rule.destination, rule.env_type) for rule in expected
    }
    assert {
        (
            rule['source']['tvm_name'],
            rule['destination']['tvm_name'],
            rule['env_type'],
        )
        for rule in content['created_rules']
    } == cache_rules
    assert response.status == 200


def _assert_mock(configs_mock, get_tvm_rules, env_types, expected_added):
    if not env_types:
        env_types = ['testing', 'production']
    env_types = set(env_types)
    expected_by_env = {}
    for env_type in env_types:
        config_rules = get_tvm_rules(env_type)['value']
        cache_rules = {(rule['src'], rule['dst']) for rule in config_rules}
        expected_cache = {
            (rule.source, rule.destination)
            for rule in expected_added
            if rule.env_type == env_type
        }
        if expected_cache:
            expected_by_env[env_type] = cache_rules | expected_cache

    calls = []
    while configs_mock.times_called:
        call = configs_mock.next_call()
        request = call['request']
        calls.append(request)

    calls = sorted(calls, key=lambda x: x.method == 'GET')

    total_env_types = len(env_types)
    for _ in range(total_env_types):
        request = calls.pop()
        env_type = _retrieve_env_type(request)
        assert request.method == 'GET', request.path
        env_types.remove(env_type)

    assert not env_types

    while calls:
        request = calls.pop()
        assert request.method == 'POST'
        env_type = _retrieve_env_type(request)
        cache_rules = {
            (rule['src'], rule['dst']) for rule in request.json['new_value']
        }
        assert len(request.json['new_value']) == len(cache_rules)
        assert request.json['old_value'] == get_tvm_rules(env_type)['value']
        assert expected_by_env.pop(env_type) == cache_rules

    assert not expected_by_env


def _retrieve_env_type(request):
    env_type = re.match(
        r'.*/(unstable|testing|production)/.*', request.path,
    ).group(1)
    return env_type


def _make_body(request_rules, env_types):
    body = {
        'rules': [
            {'source': rule.source, 'destination': rule.destination}
            for rule in request_rules
        ],
    }
    if env_types is not None:
        body['env_types'] = env_types
    return body

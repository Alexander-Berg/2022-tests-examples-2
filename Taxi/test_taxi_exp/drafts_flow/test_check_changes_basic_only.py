import itertools
from typing import NamedTuple

import jsondiff
import pytest

from test_taxi_exp.helpers import db

NAME = 'check_map_style'


def _select(client, method_name):
    if method_name == 'PUT':
        return client.put
    return client.post


class BaseCase(NamedTuple):
    get_url: str
    check_url: str
    check_method: str
    sql_file: str
    base_self_ok: bool
    base_id_text: str


def result_calculated(base, custom):
    if base:
        return True
    return base or custom


@pytest.mark.parametrize(
    'get_url, check_url, check_method, exp_patch, expected_self_ok',
    [
        pytest.param(
            get_url,
            check_url,
            check_method,
            patch,
            self_ok_always_enabled or base_self_ok and result,
            marks=(
                pytest.mark.config(
                    EXP_MAX_LIFETIME=365 * 1000,
                    EXP_BASIC_FIELDS={
                        '__default__': [
                            'match.enabled',
                            'notifications',
                            'description',
                            'clauses.*.title',
                        ],
                    },
                    EXP3_ADMIN_CONFIG={
                        'features': {
                            'common': {
                                'self_ok_always_enabled': (
                                    self_ok_always_enabled
                                ),
                            },
                        },
                    },
                ),
                pytest.mark.pgsql('taxi_exp', files=[sql_file]),
            ),
            id=','.join((message, base_id_text, id_text)),
        )
        for (
                get_url,
                check_url,
                check_method,
                sql_file,
                base_self_ok,
                base_id_text,
        ), (patch, result, id_text), (
                self_ok_always_enabled,
                message,
        ) in itertools.product(
            (  # first group of arguments - type of object
                BaseCase(
                    get_url='/v1/experiments/',
                    check_url='/v1/experiments/drafts/check/',
                    check_method='PUT',
                    sql_file='experiment.sql',
                    base_self_ok=True,
                    base_id_text='exp with enabled self_ok',
                ),
                BaseCase(
                    get_url='/v1/configs/',
                    check_url='/v1/configs/drafts/check/',
                    check_method='PUT',
                    sql_file='config.sql',
                    base_self_ok=True,
                    base_id_text='conf with enabled self_ok',
                ),
                BaseCase(
                    get_url='/v1/experiments/',
                    check_url='/v1/closed-experiments/check/',
                    check_method='POST',
                    sql_file='closed_experiment.sql',
                    base_self_ok=True,
                    base_id_text='closed exp with enabled self_ok',
                ),
                BaseCase(
                    get_url='/v1/experiments/',
                    check_url='/v1/experiments/drafts/check/',
                    check_method='PUT',
                    sql_file='experiment_non_selfok.sql',
                    base_self_ok=False,
                    base_id_text='exp with disabled self_ok',
                ),
                BaseCase(
                    get_url='/v1/configs/',
                    check_url='/v1/configs/drafts/check/',
                    check_method='PUT',
                    sql_file='config_non_selfok.sql',
                    base_self_ok=False,
                    base_id_text='conf with disabled self_ok',
                ),
                BaseCase(
                    get_url='/v1/experiments/',
                    check_url='/v1/closed-experiments/check/',
                    check_method='POST',
                    sql_file='closed_experiment_non_selfok.sql',
                    base_self_ok=False,
                    base_id_text='closed exp with disabled self_ok',
                ),
            ),
            (  # second group of arguments - change and waited self_ok
                ({}, True, 'no change'),
                (
                    {'description': 'Change description'},
                    True,
                    'description change',
                ),
                (
                    {
                        'clauses': [
                            {
                                'title': 'default',
                                'predicate': {'type': 'false'},
                                'value': {},
                            },
                        ],
                    },
                    False,
                    'clauses change',
                ),
                (
                    {'clauses': {0: {'predicate': {'type': 'false'}}}},
                    False,
                    'change predicate type in clause',
                ),
                (
                    {'clauses': {0: {'title': 'non_default'}}},
                    True,
                    'basic change title in clause',
                ),
            ),
            (  # enable/disable feature
                (False, 'checking self_ok enabled'),
                (True, 'checking self_ok disabled'),
            ),
        )
    ],
)
@pytest.mark.pgsql(
    'taxi_exp', queries=[db.ADD_CONSUMER.format('test_consumer')],
)
async def test_check_changes_basic_only(
        taxi_exp_client,
        get_url,
        check_url,
        check_method,
        exp_patch,
        expected_self_ok,
):
    response = await taxi_exp_client.get(
        get_url, headers={'X-Ya-Service-Ticket': '123'}, params={'name': NAME},
    )
    assert response.status == 200, await response.text()
    body = await response.json()
    body_after = jsondiff.patch(body, exp_patch)

    handler = _select(taxi_exp_client, check_method)
    response = await handler(
        check_url,
        headers={'X-Ya-Service-Ticket': '123'},
        params={'name': NAME, 'last_modified_at': 1},
        json=body_after,
    )
    assert response.status == 200, await response.text()
    assert (await response.json())['data']['self_ok'] == expected_self_ok

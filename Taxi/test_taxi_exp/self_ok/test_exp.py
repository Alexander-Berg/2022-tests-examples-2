import pytest

from test_taxi_exp.helpers import db

BODY = {
    'name': 'shipments_lavka',
    'last_modified_at': 200776,
    'closed': False,
    'description': '',
    'owners': ['dipterix'],
    'watchers': [],
    'self_ok': True,
    'shutdown_mode': 'instant_shutdown',
    'enable_debug': False,
    'trait_tags': [],
    'st_tickets': [],
    'biz_revision': 1,
    'match': {
        'enabled': True,
        'schema': """type: object
properties:
  enabled:
      type: boolean
      additionalProperties: false""",
        'action_time': {
            'from': '2020-11-26T21:15:00+03:00',
            'to': '2023-11-26T21:15:00+03:00',
        },
        'consumers': [{'name': 'client_protocol/zoneinfo'}],
        'applications': [
            {'name': 'android', 'version_range': {'from': '0.0.1'}},
            {'name': 'iphone', 'version_range': {'from': '5.2.0'}},
        ],
        'predicate': {'type': 'true', 'init': {}},
    },
    'created': '2020-11-26T21:21:29.465579+03:00',
    'last_manual_update': '2020-11-26T21:21:29.465579+03:00',
    'default_value': {'enabled': False},
    'clauses': [
        {
            'title': 'Всем',
            'value': {'enabled': True},
            'is_signal': False,
            'predicate': {'type': 'true', 'init': {}},
            'is_paired_signal': False,
        },
    ],
    'department': 'common',
}


def _change_1(body):
    body['match']['applications'][0]['version_range']['from'] = '1.1.1'
    return body


def _change_2(body):
    body['clauses'][0]['predicate']['type'] = 'false'
    return body


def _change_3(body):
    return body


@pytest.mark.parametrize(
    'change,expected_self_ok',
    [(_change_1, False), (_change_2, False), (_change_3, True)],
)
@pytest.mark.pgsql(
    'taxi_exp',
    queries=[
        db.ADD_CONSUMER.format('client_protocol/zoneinfo'),
        db.ADD_APPLICATION.format('android'),
        db.ADD_APPLICATION.format('iphone'),
    ],
)
@pytest.mark.config(
    EXP3_ADMIN_CONFIG={
        'features': {'common': {'self_ok_always_enabled': False}},
    },
)
async def test(taxi_exp_client, change, expected_self_ok):
    # adding experiment
    response = await taxi_exp_client.post(
        '/v1/experiments/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params={'name': 'EXPERIMENT_NAME'},
        json=BODY,
    )
    assert response.status == 200, await response.text()

    body = change(BODY)
    params = {'name': 'EXPERIMENT_NAME', 'last_modified_at': 1}
    response = await taxi_exp_client.put(
        '/v1/experiments/drafts/check/',
        headers={'YaTaxi-Api-Key': 'secret'},
        params=params,
        json=body,
    )
    resulted_body = await response.json()
    assert response.status == 200, resulted_body
    assert resulted_body['data']['self_ok'] == expected_self_ok

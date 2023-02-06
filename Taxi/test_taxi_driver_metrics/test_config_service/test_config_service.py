# pylint: disable=C0302
from collections import namedtuple
import datetime
import operator as op
import typing as tp

import bson
import pytest

from metrics_processing.rules import common as rules_common
from metrics_processing.rules.common import utils
from metrics_processing.rules_config.config_service.common.constants import (
    CONFIG_TYPE,
)
from taxi.clients.helpers import base as api_utils

RequestParams = namedtuple('RequestParams', ('url', 'method', 'body'))
Response = namedtuple('Response', ('status', 'body'))

SOME_ACTION = {
    'action': [
        {
            'tags': [{'name': 'RepositionOfferFailed', 'ttl': 86401}],
            'type': 'tagging',
        },
    ],
    'action_name': 'qwerty',
}
SOME_EVENT = {'name': 'complete', 'topic': 'order'}


def get_test_rule(
        name='test_rule',
        type_='activity',
        zone='default',
        service_name='driver-metrics',
):
    return {
        'actions': [SOME_ACTION],
        'events': [SOME_EVENT],
        'name': name,
        'type': type_,
        'zone': zone,
        'service_name': service_name,
        'updated': api_utils.time_to_iso_string_or_none(
            datetime.datetime.now(),
        ),
    }


def get_wrong_body_response(**details):
    return {
        'message': 'Wrong config body format',
        'details': details,
        'code': 'wrong_body',
    }


async def create_config_request(
        client,
        body=None,
        previous_revision_id=None,
        revision_id=None,
        protected=False,
        type_=CONFIG_TYPE.LOYALTY,
        zone='default',
        rule_name='blocking_drivers',
        headers=None,
):
    if not body:
        body = {
            'type': type_,
            'zone': zone,
            'name': rule_name,
            'protected': protected,
            'events': [SOME_EVENT],
            'service_name': 'driver-metrics',
            'actions': [SOME_ACTION],
        }

    if previous_revision_id:
        body['previous_revision_id'] = previous_revision_id

    if revision_id:
        body['revision_id'] = revision_id

    result = await client.post(
        f'/v1/config/rule/modify', json=body, headers=headers,
    )

    json_response = await result.json()
    return result.status, json_response


async def get_config_request(
        client,
        type_: tp.Optional[str] = CONFIG_TYPE.LOYALTY,
        zone: tp.Optional[str] = 'default',
        rule_name: tp.Optional[str] = 'blocking_drivers',
):

    query = {'service_name': 'driver-metrics'}

    if type_:
        query['type'] = type_
    if zone:
        query['zone'] = zone
    if rule_name:
        query['name'] = rule_name

    result = await client.post(
        '/v1/config/rule/values',
        json=query,
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    body = await result.json()
    return result.status, body


async def get_config_zone_request(
        client,
        zone: tp.Optional[str] = 'default',
        tariff: tp.Optional[str] = None,
):
    query = {'service_name': 'driver-metrics'}

    if zone:
        query['zone'] = zone
    if tariff:
        query['tariff'] = tariff

    result = await client.post(
        '/v1/config/rule/zone/values',
        json=query,
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    body = await result.json()
    return result.status, body


async def test_cache_update(web_context, mockserver):

    rules = []

    @mockserver.json_handler('/driver-metrics/v1/config/rule/values/')
    async def get_rules(*args, **kwargs):
        return {
            'items': rules,
            'last_updated': bool(rules) and rules[-1]['updated'],
        }

    # test single rule
    activity_test_rule = get_test_rule('test_rule1')
    rules = [activity_test_rule]
    await web_context.metrics_rules_config.handler.refresh_cache()
    assert utils.get_cached_rules(web_context, 'activity') == {
        'default': [
            rules_common.Rule.from_json_config(activity_test_rule, 'activity'),
        ],
    }

    # test second rule config updating
    loyalty_test_rule = get_test_rule('test_rule1', type_='loyalty')
    rules = [loyalty_test_rule]

    await web_context.metrics_rules_config.handler.refresh_cache()
    assert utils.get_cached_rules(web_context, 'loyalty') == {
        'default': [
            rules_common.Rule.from_json_config(loyalty_test_rule, 'loyalty'),
        ],
    }
    assert utils.get_cached_rules(web_context, 'activity') == {
        'default': [
            rules_common.Rule.from_json_config(activity_test_rule, 'activity'),
        ],
    }
    assert utils.get_cached_rules(web_context, 'tagging') == {'default': []}

    tagging_rule = get_test_rule('test_tag', type_='tagging')
    tagging_rule_spb = get_test_rule('test_rule', type_='tagging', zone='spb')
    new_loyalty_rule = get_test_rule('test_loyalty', type_='loyalty')
    new_loyalty_rule_spb = get_test_rule(
        'test_rule', type_='loyalty', zone='spb',
    )

    rules = [
        tagging_rule,
        tagging_rule_spb,
        new_loyalty_rule,
        new_loyalty_rule_spb,
    ]

    await web_context.metrics_rules_config.handler.refresh_cache()

    assert utils.get_cached_rules(web_context, 'loyalty') == {
        'default': [
            rules_common.Rule.from_json_config(loyalty_test_rule, 'loyalty'),
            rules_common.Rule.from_json_config(new_loyalty_rule, 'loyalty'),
        ],
        'spb': [
            rules_common.Rule.from_json_config(
                new_loyalty_rule_spb, 'loyalty',
            ),
        ],
    }
    assert utils.get_cached_rules(web_context, 'activity') == {
        'default': [
            rules_common.Rule.from_json_config(activity_test_rule, 'activity'),
        ],
    }
    assert utils.get_cached_rules(web_context, 'tagging') == {
        'default': [
            rules_common.Rule.from_json_config(tagging_rule, 'tagging'),
        ],
        'spb': [
            rules_common.Rule.from_json_config(tagging_rule_spb, 'tagging'),
        ],
    }

    assert get_rules.times_called


@pytest.mark.parametrize('is_financial', [True, False])
async def test_get_configs(
        taxi_driver_metrics, is_financial, tags_service_mock,
):
    tags_patch = tags_service_mock(tag_info={'is_financial': is_financial})

    async def create_rule():
        nonlocal previous_revision_id
        status, body = await create_config_request(
            taxi_driver_metrics, body=rule_body,
        )
        if is_financial and rule_type == 'tagging':
            assert status == 400
        else:
            previous_revision_id = body['id']

    for rule_type in ('activity', 'tagging', 'loyalty'):
        for zone in ('spb', 'moscow', 'default'):
            previous_revision_id = None
            for i in range(12):
                rule_body = {
                    'actions': [SOME_ACTION],
                    'additional_params': {'event_cnt_threshold': 2},
                    'events': [{'name': 'complete', 'topic': 'order'}],
                    'name': f'blocking_drivers_{i}',
                    'service_name': 'driver-metrics',
                    'type': rule_type,
                    'zone': zone,
                }

                await create_rule()

                if i % 2 == 0:
                    if previous_revision_id:
                        rule_body[
                            'previous_revision_id'
                        ] = previous_revision_id
                    await create_rule()

    assert tags_patch.tags_admin_tag_info.times_called == 54

    status, body = await get_config_request(
        taxi_driver_metrics,
        rule_name='blocking_drivers_0',
        type_=None,
        zone='spb',
    )

    assert status == 200

    assert len(body['items']) == 3 - int(is_financial)

    status, body = await get_config_request(
        taxi_driver_metrics, type_='loyalty', zone=None, rule_name=None,
    )

    assert status == 200
    assert len(body['items']) == 36

    status, body = await get_config_request(
        taxi_driver_metrics, type_=None, zone=None, rule_name=None,
    )

    assert status == 200
    assert len(body['items']) == 108 - 36 * int(is_financial)


DEFAULT_GEO_NODES = [
    {
        'name': 'br_root',
        'name_en': 'Basic Hierarchy',
        'name_ru': 'Базовая иерархия',
        'node_type': 'root',
    },
    {
        'name': 'br_world',
        'name_en': 'World',
        'name_ru': 'Мир',
        'node_type': 'root',
        'parent_name': 'br_root',
        'tariff_zones': ['br_izhevsk', 'moscow'],
    },
    {
        'name': 'br_moscow',
        'name_en': 'Moscow',
        'name_ru': 'Москва',
        'node_type': 'root',
        'parent_name': 'br_root',
        'tariff_zones': ['sub_moscow'],
    },
    {
        'name': 'br_izhevsk',
        'name_en': 'Izhevsk',
        'name_ru': 'Ижевск',
        'node_type': 'root',
        'parent_name': 'br_world',
        'tariff_zones': ['rivendell'],
        'region_id': '44',
    },
]


@pytest.mark.geo_nodes(DEFAULT_GEO_NODES)
@pytest.mark.config(DRIVER_METRICS_USE_AGGLOMERATIONS=True)
@pytest.mark.parametrize(
    'zone, expected',
    (
        (
            'spb',
            [
                ('blocking_drivers_0', 'spb'),
                ('blocking_drivers_1', 'spb'),
                ('blocking_drivers_2', 'spb'),
                ('blocking_drivers_3', 'default'),
                ('blocking_drivers_4', 'default'),
            ],
        ),
        (
            'moscow',
            [
                ('blocking_drivers_0', 'moscow'),
                ('blocking_drivers_1', 'moscow'),
                ('blocking_drivers_2', 'moscow'),
                ('br_root_rule', 'node:br_root'),
                ('br_world_rule', 'node:br_world'),
                ('blocking_drivers_3', 'default'),
                ('blocking_drivers_4', 'default'),
            ],
        ),
        (
            'default',
            [
                ('blocking_drivers_1', 'default'),
                ('blocking_drivers_2', 'default'),
                ('blocking_drivers_3', 'default'),
                ('blocking_drivers_4', 'default'),
            ],
        ),
        (
            'node:br_world',
            [
                ('br_world_rule', 'node:br_world'),
                ('blocking_drivers_1', 'default'),
                ('blocking_drivers_2', 'default'),
                ('blocking_drivers_3', 'default'),
                ('blocking_drivers_4', 'default'),
            ],
        ),
        (
            'rivendell',
            [
                ('br_izhevsk_rule', 'node:br_izhevsk'),
                ('br_root_rule', 'node:br_root'),
                ('br_world_rule', 'node:br_world'),
                ('blocking_drivers_1', 'default'),
                ('blocking_drivers_2', 'default'),
                ('blocking_drivers_3', 'default'),
                ('blocking_drivers_4', 'default'),
            ],
        ),
        (
            'br_izhevsk',
            [
                ('br_root_rule', 'node:br_root'),
                ('br_world_rule', 'node:br_world'),
                ('blocking_drivers_1', 'default'),
                ('blocking_drivers_2', 'default'),
                ('blocking_drivers_3', 'default'),
                ('blocking_drivers_4', 'default'),
            ],
        ),
        (
            'fake',
            [
                ('blocking_drivers_1', 'default'),
                ('blocking_drivers_2', 'default'),
                ('blocking_drivers_3', 'default'),
                ('blocking_drivers_4', 'default'),
            ],
        ),
        (None, None),
    ),
)
async def test_get_zone_configs(
        taxi_driver_metrics, tags_service_mock, zone, expected,
):
    async def create_rule():
        await create_config_request(taxi_driver_metrics, body=rule_body)

    for rule_zone in ('spb', 'moscow'):
        for i in range(3):
            rule_body = {
                'actions': [SOME_ACTION],
                'events': [SOME_EVENT],
                'name': f'blocking_drivers_{i}',
                'additional_params': {'expr': 'True'},
                'service_name': 'driver-metrics',
                'type': 'activity',
                'zone': rule_zone,
            }

            await create_rule()

    for create_rule_zone in ('br_root', 'br_world', 'br_izhevsk'):
        rule_body = {
            'actions': [SOME_ACTION],
            'events': [SOME_EVENT],
            'name': f'{create_rule_zone}_rule',
            'service_name': 'driver-metrics',
            'type': 'activity',
            'zone': f'node:{create_rule_zone}',
        }

        await create_rule()

    for i in range(1, 5):
        rule_body = {
            'actions': [SOME_ACTION],
            'events': [SOME_EVENT],
            'name': f'blocking_drivers_{i}',
            'service_name': 'driver-metrics',
            'type': 'activity',
            'zone': 'default',
        }

        await create_rule()

    def get_rule_data(rules):
        for rule in rules:
            assert rule.get('id')
        return list(map(op.itemgetter('name', 'zone'), rules))

    status, body = await get_config_zone_request(
        taxi_driver_metrics, zone=zone,
    )

    if not expected:
        assert status == 400
    else:
        assert get_rule_data(body['items']) == expected


def extract_fields(
        values: tp.List[tp.Dict], fields: tp.Collection[str],
) -> tp.List:
    return list(map(op.itemgetter(*fields), values))


@pytest.mark.geo_nodes(DEFAULT_GEO_NODES)
@pytest.mark.config(DRIVER_METRICS_USE_AGGLOMERATIONS=True)
@pytest.mark.config(
    DRIVER_METRICS_TARIFF_TOPOLOGIES={
        '__default__': {'__default__': {'__default__': ['__default__']}},
        'driver-metrics': {
            '__default__': {'comfort': ['comfort', 'economy']},
            'node:br_izhevsk': {'comfort': ['children', 'comfort']},
        },
    },
)
@pytest.mark.parametrize(
    'zone, tariff, expected',
    [
        pytest.param(
            'node:br_world',
            'comfort',
            [('br_world_rule', 'node:br_world', 'comfort')],
            id='chained_tariff',
        ),
        pytest.param(
            'node:br_world',
            'children',
            [('br_world_rule', 'node:br_world', '__default__')],
            id='unknown_tariff',
        ),
        pytest.param(
            'node:br_world',
            None,
            [('br_world_rule', 'node:br_world', 'children')],
            id='no_tariff_eq_last_tariff',
        ),
        pytest.param(
            'rivendell',
            '__default__',
            [
                ('br_izhevsk_rule', 'node:br_izhevsk', '__default__'),
                ('br_root_rule', 'node:br_root', '__default__'),
                ('br_world_rule', 'node:br_world', '__default__'),
            ],
            id='default_tariff',
        ),
        pytest.param(
            'br_izhevsk',
            '__default__',
            [
                ('br_root_rule', 'node:br_root', '__default__'),
                ('br_world_rule', 'node:br_world', '__default__'),
            ],
            id='br_izhevsk',
        ),
        pytest.param(
            'rivendell',
            'comfort',
            [
                ('br_izhevsk_rule', 'node:br_izhevsk', 'children'),
                ('br_root_rule', 'node:br_root', 'comfort'),
                ('br_world_rule', 'node:br_world', 'comfort'),
            ],
            id='zone_override',
        ),
    ],
)
async def test_get_zone_configs_tariff(
        taxi_driver_metrics, tags_service_mock, zone, tariff, expected,
):
    for rule_zone in ('br_root', 'br_world', 'br_izhevsk'):
        for rule_tariff in ('comfort', 'economy', '__default__', 'children'):
            rule_body = {
                'actions': [SOME_ACTION],
                'events': [SOME_EVENT],
                'additional_params': {'events_to_trigger_cnt': 2},
                'name': f'{rule_zone}_rule',
                'service_name': 'driver-metrics',
                'type': 'activity',
                'zone': f'node:{rule_zone}',
                'tariff': rule_tariff,
            }

            await create_config_request(taxi_driver_metrics, body=rule_body)

    status, body = await get_config_zone_request(
        taxi_driver_metrics, zone=zone, tariff=tariff,
    )

    if expected is None:
        assert status == 400
    else:
        assert (
            extract_fields(body['items'], ('name', 'zone', 'tariff'))
            == expected
        )
        assert all(
            [
                rule['additional_params']['events_to_trigger_cnt'] == 2
                for rule in body['items']
            ],
        )


@pytest.mark.parametrize(
    'draft_handler, draft_check_handler',
    (
        ('/v1/config/draft/apply', '/v1/config/draft/check'),
        ('/v1/config/draft/apply', '/v1/config/audited/draft/check'),
    ),
)
async def test_drafts(
        taxi_driver_metrics,
        mockserver,
        web_context,
        draft_handler,
        draft_check_handler,
):
    rule_body = {
        'actions': [SOME_ACTION],
        'additional_params': {'events_to_trigger_cnt': 2},
        'events': [SOME_EVENT],
        'name': f'blocking_drivers_1',
        'type': 'activity',
        'service_name': 'driver-metrics',
        'responsible_staff_login': 'abd-damir',
        'importance': 'tier_1',
        'deadline_seconds': 120,
        'query': 'SELECT * FROM $order_metrics',
        'zone': 'spb',
        'protected': True,
        'deleted': False,
        'tariff': '__default__',
    }

    async def create_rule(rule_body):
        return await create_config_request(
            taxi_driver_metrics,
            body=rule_body,
            headers={'X-Ya-Service-Ticket': 'ticket'},
        )

    status, result = await create_rule(rule_body)
    assert status == 200
    rule_id = result['id']

    rule_body['revision_id'] = rule_id
    rule_body['additional_params'] = {}

    result = await taxi_driver_metrics.post(
        draft_check_handler,
        json={'new': rule_body},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    new_rule = {
        'name': 'blocking_drivers_1',
        'zone': 'spb',
        'type': 'activity',
        'events': [SOME_EVENT],
        'actions': [SOME_ACTION],
        'additional_params': {},
        'service_name': 'driver-metrics',
        'revision_id': rule_id,
        'disabled': False,
        'responsible_staff_login': 'abd-damir',
        'importance': 'tier_1',
        'deadline_seconds': 120,
        'query': 'SELECT * FROM $order_metrics',
        'delayed': False,
        # Cannot create protected rule from modify api
        'protected': True,
        'deleted': False,
        'tariff': '__default__',
    }

    old_rule = {
        'name': 'blocking_drivers_1',
        'zone': 'spb',
        'type': 'activity',
        'events': [SOME_EVENT],
        'actions': [SOME_ACTION],
        'additional_params': {'events_to_trigger_cnt': 2},
        'service_name': 'driver-metrics',
        'revision_id': rule_id,
        'delayed': False,
        'disabled': False,
        'responsible_staff_login': 'abd-damir',
        'importance': 'tier_1',
        'deadline_seconds': 120,
        'deleted': False,
        'protected': False,
        'query': 'SELECT * FROM $order_metrics',
        'tariff': '__default__',
    }

    assert result.status == 200
    json = await result.json()

    change_doc_id = json.pop('change_doc_id')

    assert change_doc_id.startswith('spb:')

    del json['diff']['current']['updated']

    assert json == {
        'diff': {'current': old_rule, 'new': new_rule},
        'data': {'new': new_rule},
    }

    await taxi_driver_metrics.post(
        draft_handler,
        json={'new': new_rule},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    status, result = await get_config_request(
        taxi_driver_metrics,
        rule_name='blocking_drivers_1',
        type_='activity',
        zone='spb',
    )

    assert status == 200
    del result['items'][0]['updated']
    del result['items'][0]['id']
    del result['last_updated']
    assert result == {
        'items': [
            {
                'actions': [SOME_ACTION],
                'additional_params': {},
                'disabled': False,
                'responsible_staff_login': 'abd-damir',
                'importance': 'tier_1',
                'deadline_seconds': 120,
                'delayed': False,
                'events': [SOME_EVENT],
                'name': 'blocking_drivers_1',
                'service_name': 'driver-metrics',
                'protected': True,
                'deleted': False,
                'type': 'activity',
                'query': 'SELECT * FROM $order_metrics',
                'zone': 'spb',
                'tariff': '__default__',
            },
        ],
    }

    history = []

    db = web_context.mongo

    async for rule in db.driver_metrics_rules_configs_history.find():
        del rule['_id']
        assert rule.pop('updated')
        history.append(rule)

    assert history == [
        {
            'actions': [SOME_ACTION],
            'additional_params': {'events_to_trigger_cnt': 2},
            'disabled': False,
            'responsible_staff_login': 'abd-damir',
            'importance': 'tier_1',
            'deadline_seconds': 120,
            'delayed': False,
            'events': [SOME_EVENT],
            'name': 'blocking_drivers_1',
            'protected': False,
            'service_name': 'driver-metrics',
            'type': 'activity',
            'deleted': False,
            'zone': 'spb',
            'query': 'SELECT * FROM $order_metrics',
            'revision_id': bson.ObjectId(rule_id),
            'tariff': '__default__',
        },
    ]


@pytest.mark.now('2016-12-31T00:00:00')
async def test_config_common_old(taxi_driver_metrics):
    # Wrong format saving test
    status, body = await create_config_request(taxi_driver_metrics, type_=None)

    assert status == 400
    assert body == {
        'code': 'invalid-input',
        'details': {
            'type': [
                'None is not one of [\'loyalty\', \'tagging\', \'activity\', '
                '\'default\', \'communications\', \'query\', '
                '\'dispatch_length_thresholds\', '
                '\'blocking\', \'stq_callback\', \'activity_blocking\']',
                'None is not of type \'string\'',
            ],
        },
        'message': 'Invalid input',
        'status': 'error',
    }

    # Correct saving test

    status, body = await create_config_request(taxi_driver_metrics)

    assert status == 200
    correct_revision_id = body['id']

    status, body = await get_config_request(taxi_driver_metrics)
    assert status == 200
    del body['items'][0]['updated']
    del body['last_updated']
    assert body == {
        'items': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'tags': [
                                    {
                                        'name': 'RepositionOfferFailed',
                                        'ttl': 86401,
                                    },
                                ],
                                'type': 'tagging',
                            },
                        ],
                        'action_name': 'qwerty',
                    },
                ],
                'events': [{'name': 'complete', 'topic': 'order'}],
                'id': correct_revision_id,
                'service_name': 'driver-metrics',
                'additional_params': {},
                'disabled': False,
                'deleted': False,
                'type': 'loyalty',
                'tariff': '__default__',
                'zone': 'default',
                'name': 'blocking_drivers',
                'protected': False,
                'delayed': False,
            },
        ],
    }

    # Saving with wrong revision id test

    status, body = await create_config_request(taxi_driver_metrics)

    assert status == 409
    assert body == {
        'code': 'old_revision',
        'details': None,
        'message': 'Config has a newer ' 'revision than updating data',
    }

    # Saving with actual revision

    status, body = await create_config_request(
        taxi_driver_metrics, previous_revision_id=correct_revision_id,
    )

    assert status == 200
    incorrect_revision_id = correct_revision_id
    new_correct_value = body['id']

    # Saving with revision

    status, body = await create_config_request(
        taxi_driver_metrics, previous_revision_id=incorrect_revision_id,
    )

    assert status == 400

    # Getting actual revision test

    status, body = await get_config_request(taxi_driver_metrics)

    assert status == 200
    del body['items'][0]['updated']
    del body['last_updated']
    assert body == {
        'items': [
            {
                'actions': [
                    {
                        'action': [
                            {
                                'tags': [
                                    {
                                        'name': 'RepositionOfferFailed',
                                        'ttl': 86401,
                                    },
                                ],
                                'type': 'tagging',
                            },
                        ],
                        'action_name': 'qwerty',
                    },
                ],
                'additional_params': {},
                'events': [{'name': 'complete', 'topic': 'order'}],
                'id': new_correct_value,
                'name': 'blocking_drivers',
                'type': 'loyalty',
                'disabled': False,
                'deleted': False,
                'tariff': '__default__',
                'zone': 'default',
                'service_name': 'driver-metrics',
                'protected': False,
                'delayed': False,
            },
        ],
    }

    # Saving with wrong revision id test

    status, body = await create_config_request(
        taxi_driver_metrics, previous_revision_id='fake',
    )

    assert status == 400
    assert body == {
        'code': 'incorrect_revision',
        'details': {'previous_revision_id': 'fake'},
        'message': 'Previous revision ID is incorrect',
    }

    # Saving with actual revision
    status, body = await create_config_request(
        taxi_driver_metrics, type_='activity',
    )

    assert status == 200


@pytest.mark.config(TVM_ENABLED=True)
async def test_drafts_forbidden(web_app_client, patch):
    rule_body = {
        'actions': [SOME_ACTION],
        'additional_params': {'events_to_trigger_cnt': 2},
        'events': [SOME_EVENT],
        'name': f'blocking_drivers_1',
        'type': 'activity',
        'service_name': 'driver-metrics',
        'zone': 'spb',
        'protected': True,
    }

    @patch('taxi.clients.tvm.TVMClient.get_allowed_service_name')
    async def get_ticket(*args, **kwargs):
        return 'fake'

    async def create_rule(rule_body):
        return await create_config_request(
            web_app_client,
            body=rule_body,
            headers={'X-Ya-Service-Ticket': 'ticket'},
        )

    status, result = await create_rule(rule_body)

    assert status == 200

    result = await web_app_client.post(
        '/v1/config/draft/apply',
        json={'new': rule_body},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    assert get_ticket.calls
    assert result.status == 403


async def test_update_config_locally(
        web_context, taxi_driver_metrics, dm_mockserver,
):
    status, _ = await create_config_request(taxi_driver_metrics)

    assert status == 200

    await web_context.metrics_rules_config.handler.refresh_cache_locally()

    rules = utils.get_cached_rules(web_context, 'loyalty')['default']
    assert 'blocking_drivers' in {rule.name for rule in rules}

    times_called = dm_mockserver.handler.times_called

    await web_context.on_startup()
    # Config rules have not been called
    assert times_called == dm_mockserver.handler.times_called


async def test_get_zones(taxi_driver_metrics, tags_service_mock):
    async def create_rule(zone, **kwargs):
        await create_config_request(taxi_driver_metrics, zone=zone, **kwargs)

    for zone in ('spb', 'moscow', 'default'):
        await create_rule(zone=zone)

    result = await taxi_driver_metrics.post(
        '/v1/config/rule/zones/',
        json={'service_name': 'driver-metrics'},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )

    assert result.status == 200
    json = await result.json()
    assert json == {'zones': ['default', 'moscow', 'spb']}

    await create_rule(zone='node:br_moscow')

    result = await taxi_driver_metrics.post(
        '/v1/config/rule/zones/',
        json={'service_name': 'driver-metrics'},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )
    assert result.status == 200
    json = await result.json()
    assert json == {'zones': ['default', 'moscow', 'node:br_moscow', 'spb']}

    await create_rule(zone='node:br_root', type_='activity')

    result = await taxi_driver_metrics.post(
        '/v1/config/rule/zones/',
        json={'service_name': 'driver-metrics', 'rule_type': 'activity'},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )
    assert result.status == 400

    result = await taxi_driver_metrics.post(
        '/v1/config/rule/zones/',
        json={'service_name': 'driver-metrics', 'type': 'activity'},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )
    assert result.status == 200
    json = await result.json()
    assert json == {'zones': ['node:br_root']}


@pytest.mark.parametrize(
    'service_name, expected',
    [
        pytest.param(
            'driver-metrics', {'tariffs': ['__default__']}, id='default',
        ),
        pytest.param(
            'rider-metrics',
            {'tariffs': ['children', 'comfort', 'econom']},
            id='multiple_tariffs',
        ),
    ],
)
@pytest.mark.config(
    DRIVER_METRICS_TARIFF_LISTS={
        '__default__': ['__default__'],
        'rider-metrics': ['econom', 'comfort', 'children'],
    },
)
async def test_get_tariffs(
        taxi_driver_metrics, tags_service_mock, service_name, expected,
):
    result = await taxi_driver_metrics.post(
        '/v1/config/rule/tariffs/',
        json={'service_name': service_name},
        headers={'X-Ya-Service-Ticket': 'ticket'},
    )
    assert result.status == 200
    data = await result.json()
    assert data == expected

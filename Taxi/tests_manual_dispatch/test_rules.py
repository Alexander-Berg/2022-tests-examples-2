# pylint: disable=redefined-outer-name
import datetime

import pytest


def normalize_phone(phone):
    return ''.join(x for x in phone if x not in '() -')


def contact_to_pg(contact):
    if contact is None:
        return None
    # pgsql doesn't handle composite types very well
    contact['phone_number'] = normalize_phone(contact['phone_number'])
    return f'("{contact["name"]}",{contact["phone_number"]}_id)'


def request_rule_to_db(rule, rule_id, client_id):
    return {
        'main_contact': contact_to_pg(rule.get('main_contact')),
        'backup_contact': contact_to_pg(rule.get('backup_contact')),
        'client_id': client_id,
        'tariffs': sorted(rule['tariffs']),
        'is_enabled': rule['is_enabled'],
        'new_list_hit_flow': True,
        'lookup_ttl': datetime.timedelta(seconds=rule['lookup_ttl']),
        'switch_interval': datetime.timedelta(
            seconds=rule['manual_switch_interval'],
        ),
        'id': rule_id,
        'name': rule['name'],
    }


@pytest.mark.parametrize(
    ['request_body', 'response_code', 'error_code'],
    [
        (
            {
                'is_corp_enabled': True,
                'rules': [
                    {
                        'rule': {
                            'name': 'name_1',
                            'tariffs': ['comfort', 'comfortplus'],
                            'is_enabled': False,
                            'new_list_hit_flow': True,
                            'lookup_ttl': 0,
                            'manual_switch_interval': 100,
                        },
                    },
                    {
                        'rule': {
                            'name': 'name_2',
                            'tariffs': ['courier'],
                            'is_enabled': False,
                            'new_list_hit_flow': True,
                            'lookup_ttl': 0,
                            'manual_switch_interval': 100,
                            'main_contact': {
                                'phone_number': '+7 (123) 456-78-9012',
                                'name': 'Foo Bar',
                            },
                            'backup_contact': {
                                'phone_number': '+7123456789012',
                                'name': 'Spam Eggs',
                            },
                        },
                    },
                ],
            },
            200,
            None,
        ),
        (
            {
                'is_corp_enabled': False,
                'rules': [
                    {
                        'rule': {
                            'name': 'name_1',
                            'tariffs': ['comfort', 'comfortplus'],
                            'is_enabled': False,
                            'new_list_hit_flow': True,
                            'lookup_ttl': None,
                            'manual_switch_interval': 100,
                        },
                    },
                    {
                        'rule': {
                            'name': 'name_2',
                            'tariffs': ['comfort'],
                            'is_enabled': False,
                            'new_list_hit_flow': True,
                            'lookup_ttl': 0,
                            'manual_switch_interval': 100,
                        },
                    },
                ],
            },
            400,
            'duplicate_rule_and_tariff',
        ),
    ],
)
async def test_edit(
        taxi_manual_dispatch,
        headers,
        mockserver,
        get_rules,
        get_client,
        request_body,
        response_code,
        error_code,
):
    client_id = 'client_id_1'

    @mockserver.json_handler('/taxi-corp-integration/v1/client')
    def _client(*args, **kwargs):
        return {
            'client_id': client_id,
            'contract_id': 'contract_id',
            'name': 'client_name',
            'billing_contract_id': '123',
            'billing_client_id': '123',
            'country': 'rus',
            'services': {},
        }

    response = await taxi_manual_dispatch.post(
        '/v1/rules/edit',
        request_body,
        headers={**headers, 'X-B2B-Client-Id': client_id},
    )

    assert response.status_code == response_code
    response_body = response.json()
    if response_code == 200:
        client = get_client(client_id)
        assert client['name'] == 'client_name'
        assert client['is_enabled'] == response_body['is_corp_enabled']
        assert (
            response_body['is_corp_enabled'] == request_body['is_corp_enabled']
        )

        for request_rule, response_rule in zip(
                request_body['rules'], response_body['rules'],
        ):
            if 'main_contact' in request_rule['rule']:
                request_rule['rule']['main_contact']['phone_number'] = (
                    normalize_phone(
                        request_rule['rule']['main_contact']['phone_number'],
                    )
                )
            assert request_rule['rule'] == response_rule['rule']
            assert 'id' in response_rule

        def sorted_rules(rules):
            return sorted(rules, key=lambda x: x['id'])

        assert sorted_rules(get_rules(client_id)) == [
            request_rule_to_db(x['rule'], x['id'], client_id)
            for x in sorted_rules(response_body['rules'])
        ]
    else:
        assert response_body['code'] == error_code


async def test_list(taxi_manual_dispatch, headers, get_rules):
    client_id = 'client_id_1'

    response = await taxi_manual_dispatch.post(
        '/v1/rules/list',
        {'client_id': client_id},
        headers={**headers, 'X-B2B-Client-Id': client_id},
    )

    assert response.status_code == 200
    response_body = response.json()
    response_body['rules'][1]['rule']['tariffs'] = set(
        response_body['rules'][1]['rule']['tariffs'],
    )
    assert response_body == {
        'is_corp_enabled': True,
        'rules': [
            {
                'id': 'rule_id_2',
                'rule': {
                    'backup_contact': {
                        'name': 'Spam Eggs',
                        'phone_number': '+7123456789012',
                    },
                    'main_contact': {
                        'name': 'Baz Buzz',
                        'phone_number': '+7123456789012',
                    },
                    'is_enabled': True,
                    'new_list_hit_flow': False,
                    'lookup_ttl': 1800,
                    'manual_switch_interval': 1800,
                    'name': 'name_2',
                    'tariffs': ['courier'],
                },
            },
            {
                'id': 'rule_id_1',
                'rule': {
                    'main_contact': {
                        'name': 'Foo Bar',
                        'phone_number': '+700012345678',
                    },
                    'is_enabled': True,
                    'new_list_hit_flow': False,
                    'lookup_ttl': 1800,
                    'manual_switch_interval': 1800,
                    'name': 'name_1',
                    'tariffs': set(['econom', 'comfort']),
                },
            },
        ],
    }

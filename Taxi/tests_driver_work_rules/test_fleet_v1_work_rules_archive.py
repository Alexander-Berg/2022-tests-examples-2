import json

import pytest

from tests_driver_work_rules import changelog
from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils

ENDPOINT = 'fleet/driver-work-rules/v1/work-rules/archive'

TEST_PUT_PARAMS = [
    (
        'extra_super_park_id',
        'work_rule_id_archived',
        {'is_archived': False},
        204,
        None,
        utils.modify_base_dict(
            defaults.BASE_PG_WORK_RULE, {'is_archived': False},
        ),
        json.dumps({'IsArchived': {'current': 'False', 'old': 'True'}}),
        True,
    ),
    (
        'extra_super_park_id',
        'work_rule_id_active',
        {'is_archived': True},
        204,
        None,
        utils.modify_base_dict(
            defaults.BASE_PG_WORK_RULE, {'is_archived': True},
        ),
        json.dumps({'IsArchived': {'current': 'True', 'old': 'False'}}),
        True,
    ),
    (
        'extra_super_park_id',
        'work_rule_id_archived',
        {'is_archived': True},
        204,
        None,
        utils.modify_base_dict(
            defaults.BASE_PG_WORK_RULE, {'is_archived': True},
        ),
        None,
        False,
    ),
    (
        'extra_super_park_id',
        'work_rule_id_default',
        {'is_archived': True},
        400,
        {
            'code': 'rule_сan_not_be_default_and_archived',
            'message': 'Rule can not be default and archived simultaneously',
        },
        None,
        None,
        True,
    ),
    (
        'not_existing_park',
        'work_rule_id',
        {'is_archived': True},
        404,
        {
            'code': 'not_found',
            'message': 'Rule with id `work_rule_id` not found',
        },
        None,
        None,
        True,
    ),
    (
        'extra_super_park_id',
        'not_existing_work_rule_id',
        {'is_archived': True},
        404,
        {
            'code': 'not_found',
            'message': 'Rule with id `not_existing_work_rule_id` not found',
        },
        None,
        None,
        True,
    ),
]


@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.parametrize(
    'park_id,rule_id,request_body,expected_status_code,expected_response,'
    'expected_pg_work_rule, expected_changelog_entry,check_updated_at',
    TEST_PUT_PARAMS,
)
async def test_put(
        taxi_driver_work_rules,
        fleet_parks_shard,
        pgsql,
        park_id,
        rule_id,
        request_body,
        expected_status_code,
        expected_response,
        expected_pg_work_rule,
        expected_changelog_entry,
        check_updated_at,
):
    response = await taxi_driver_work_rules.put(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS, {'X-Park-Id': park_id},
        ),
        params={'work_rule_id': rule_id},
        json=request_body,
    )
    assert response.status_code == expected_status_code, response.text
    if expected_response is not None:
        assert response.json() == expected_response

    if expected_pg_work_rule is not None:
        pg_work_rule = utils.get_postgres_work_rule(pgsql, park_id, rule_id)
        pg_work_rule.pop('created_at')
        updated_at = pg_work_rule.pop('updated_at')
        if check_updated_at:
            utils.check_updated_at(updated_at)
        pg_work_rule.pop('id')
        assert pg_work_rule == expected_pg_work_rule

    # pg changelog entry
    log_info = utils.modify_base_dict(
        defaults.LOG_INFO, {'counts': 1, 'ip': '', 'park_id': park_id},
    )
    changelog.check_work_rule_changes(
        pgsql, log_info, expected_changelog_entry,
    )


async def test_user_not_registered_in_park(mockserver, taxi_driver_work_rules):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _get_users_list(request):
        return {'users': []}

    response = await taxi_driver_work_rules.put(
        ENDPOINT,
        headers=defaults.HEADERS,
        params={'work_rule_id': ''},
        json={'is_archived': True},
    )
    assert response.status_code == 403
    assert response.json() == {
        'code': 'user_not_registered_in_park',
        'message': 'Users is not registered in park',
    }


TEST_VEZET_PARAMS = [
    (
        'yandex',
        '',
        403,
        {'code': 'no_permissions', 'message': 'No permissions'},
    ),
    (
        'yandex_team',
        '',
        403,
        {'code': 'no_permissions', 'message': 'No permissions'},
    ),
    (
        'yandex_team',
        'work_rules_type_ne_vezet',
        403,
        {'code': 'no_permissions', 'message': 'No permissions'},
    ),
    (
        'yandex_team',
        'work_rules_type_ne_vezet,work_rules_type_vezet,work_rules_type_vezet_inogda',  # noqa: E501
        204,
        None,
    ),
]


@pytest.mark.pgsql('driver-work-rules', files=['work_rules_vezet.sql'])
@pytest.mark.parametrize(
    (
        'user_provider',
        'permissions',
        'expected_status_code',
        'expected_response',
    ),
    TEST_VEZET_PARAMS,
)
async def test_vezet(
        taxi_driver_work_rules,
        fleet_parks_shard,
        pgsql,
        user_provider,
        permissions,
        expected_status_code,
        expected_response,
):
    response = await taxi_driver_work_rules.put(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS,
            {
                'X-Park-Id': 'extra_super_park_id',
                'X-Ya-User-Ticket-Provider': user_provider,
                'X-YaTaxi-Fleet-Permissions': permissions,
            },
        ),
        params={'work_rule_id': 'work_rule_id_archived'},
        json={'is_archived': False},
    )
    assert response.status_code == expected_status_code, response.text
    if expected_response is not None:
        assert response.json() == expected_response

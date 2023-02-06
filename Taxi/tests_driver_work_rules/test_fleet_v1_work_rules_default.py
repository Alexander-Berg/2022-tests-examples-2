import json

import pytest

from tests_driver_work_rules import changelog
from tests_driver_work_rules import defaults
from tests_driver_work_rules import utils

ENDPOINT = 'fleet/driver-work-rules/v1/work-rules/default'

TEST_GET_PARAMS = [
    (
        'park_with_default_rule',
        200,
        {'id': 'work_rule_id_default', 'name': 'Name'},
    ),
    (
        'park_without_default_rule',
        404,
        {'code': 'not_found', 'message': 'Park hasn\'t default work rule'},
    ),
    (
        'not_existing_park',
        404,
        {'code': 'not_found', 'message': 'Park hasn\'t default work rule'},
    ),
]


@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.parametrize(
    'park_id,expected_status_code,expected_response', TEST_GET_PARAMS,
)
async def test_get(
        taxi_driver_work_rules,
        park_id,
        expected_status_code,
        expected_response,
):
    response = await taxi_driver_work_rules.get(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS, {'X-Park-Id': park_id},
        ),
    )

    assert response.status_code == expected_status_code, response.text
    assert response.json() == expected_response


TEST_POST_PARAMS = [
    (
        'park_with_default_rule',
        'work_rule_id_default',
        204,
        None,
        utils.modify_base_dict(
            defaults.BASE_PG_WORK_RULE,
            {'park_id': 'park_with_default_rule', 'is_default': True},
        ),
        'work_rule_id_default',
        True,
        {},
        False,
    ),
    (
        'park_with_default_rule',
        'work_rule_id_not_default',
        204,
        None,
        utils.modify_base_dict(
            defaults.BASE_PG_WORK_RULE,
            {'park_id': 'park_with_default_rule', 'is_default': True},
        ),
        'work_rule_id_default',
        False,
        {
            'work_rule_id_not_default': json.dumps(
                {'IsDefault': {'current': 'True', 'old': 'False'}},
            ),
            'work_rule_id_default': json.dumps(
                {'IsDefault': {'current': 'False', 'old': 'True'}},
            ),
        },
        True,
    ),
    (
        'park_without_default_rule',
        'work_rule_id_not_default',
        204,
        None,
        utils.modify_base_dict(
            defaults.BASE_PG_WORK_RULE,
            {'park_id': 'park_without_default_rule', 'is_default': True},
        ),
        None,
        False,
        {
            'work_rule_id_not_default': json.dumps(
                {'IsDefault': {'current': 'True', 'old': 'False'}},
            ),
        },
        True,
    ),
    (
        'park_without_default_rule',
        'work_rule_id_archived',
        400,
        {
            'code': 'rule_сan_not_be_default_and_archived',
            'message': 'Rule can not be default and archived simultaneously',
        },
        None,
        None,
        None,
        {},
        True,
    ),
    (
        'not_existing_park',
        'work_rule_id_not_default',
        404,
        {
            'code': 'not_found',
            'message': 'Rule with id `work_rule_id_not_default` not found',
        },
        None,
        None,
        None,
        {},
        True,
    ),
    (
        'park_with_default_rule',
        'not_existing_work_rule_id',
        404,
        {
            'code': 'not_found',
            'message': 'Rule with id `not_existing_work_rule_id` not found',
        },
        None,
        None,
        None,
        {},
        True,
    ),
]


@pytest.mark.pgsql('driver-work-rules', files=['work_rules.sql'])
@pytest.mark.parametrize(
    'park_id,work_rule_id,expected_status_code,expected_response,'
    'expected_pg_work_rule,old_default_rule_id,expected_old_rule_is_default,'
    'expected_changelog_entries,check_updated_at',
    TEST_POST_PARAMS,
)
async def test_post(
        fleet_parks_shard,
        taxi_driver_work_rules,
        pgsql,
        park_id,
        work_rule_id,
        expected_status_code,
        expected_response,
        expected_pg_work_rule,
        old_default_rule_id,
        expected_old_rule_is_default,
        expected_changelog_entries,
        check_updated_at,
):
    # response
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS, {'X-Park-Id': park_id},
        ),
        params={'work_rule_id': work_rule_id},
    )
    assert response.status_code == expected_status_code, response.text
    if expected_response is not None:
        assert response.json() == expected_response

    # pg work rule entity
    if expected_pg_work_rule is not None:
        pg_work_rule = utils.get_postgres_work_rule(
            pgsql, park_id, work_rule_id,
        )
        pg_work_rule.pop('created_at')

        updated_at = pg_work_rule.pop('updated_at')
        if check_updated_at:
            utils.check_updated_at(updated_at)

        pg_work_rule.pop('id')
        assert pg_work_rule == expected_pg_work_rule

    if old_default_rule_id is not None:
        old_default_rule = utils.get_postgres_work_rule(
            pgsql, park_id, old_default_rule_id,
        )
        assert old_default_rule['is_default'] == expected_old_rule_is_default
        if check_updated_at:
            utils.check_updated_at(old_default_rule['updated_at'])

    # pg changelog entry
    log_info = utils.modify_base_dict(
        defaults.LOG_INFO, {'counts': 1, 'ip': '', 'park_id': park_id},
    )
    changelog.check_work_rules_changes(
        pgsql, log_info, expected_changelog_entries,
    )


async def test_user_not_registered_in_park(mockserver, taxi_driver_work_rules):
    @mockserver.json_handler('/dispatcher-access-control/v1/parks/users/list')
    def _get_users_list(request):
        return {'users': []}

    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        headers=defaults.HEADERS,
        params={'work_rule_id': 'work_rule_id_not_default'},
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
        fleet_parks_shard,
        taxi_driver_work_rules,
        pgsql,
        user_provider,
        permissions,
        expected_status_code,
        expected_response,
):
    # response
    response = await taxi_driver_work_rules.post(
        ENDPOINT,
        headers=utils.modify_base_dict(
            defaults.HEADERS,
            {
                'X-Park-Id': 'park_with_default_rule',
                'X-Ya-User-Ticket-Provider': user_provider,
                'X-YaTaxi-Fleet-Permissions': permissions,
            },
        ),
        params={'work_rule_id': 'work_rule_id_default'},
    )
    assert response.status_code == expected_status_code
    if expected_response is not None:
        assert response.json() == expected_response

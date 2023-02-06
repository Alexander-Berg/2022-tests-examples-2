import pytest

from tests_access_control.helpers import admin_permission_calculation_rules


@pytest.mark.pgsql('access_control', files=['system/group1.sql'])
async def test_create_permission_calculation_rules_success(
        taxi_access_control,
):
    await admin_permission_calculation_rules.create_calculation_rule(
        taxi_access_control,
        'group1',
        'permission-calculation-rule-name',
        'query',
        'fake-path',
        expected_status_code=200,
        expected_response_json={
            'id': 1,
            'slug': 'permission-calculation-rule-name',
            'path': 'fake-path',
            'storage': 'query',
            'system_slug': 'group1',
            'version': 1,
        },
    )


@pytest.mark.pgsql(
    'access_control',
    files=[
        'system/group1.sql',
        'permission_calculation_rules/permission_calculation_rule1_group1.sql',
    ],
)
async def test_create_permission_calculation_rule_conflict_same_rule(
        taxi_access_control,
):
    await admin_permission_calculation_rules.create_calculation_rule(
        taxi_access_control,
        'group1',
        'permission-calculation-rule-1',
        'query',
        'fake-path',
        expected_status_code=409,
        expected_response_json={
            'code': 'already_exist',
            'message': 'Permission Calculation Rule already exist',
        },
    )


@pytest.mark.pgsql('access_control', files=['system/group1.sql'])
async def test_create_permission_calculation_rules_invalid_storage(
        taxi_access_control,
):
    await admin_permission_calculation_rules.create_calculation_rule(
        taxi_access_control,
        'group1',
        'permission-calculation-rule-name',
        'invalid-storage',
        'fake-path',
        expected_status_code=400,
        expected_response_json={
            'code': '400',
            'message': (
                'Value of \'storage\' (invalid-storage) '
                'is not parseable into enum'
            ),
        },
    )


async def test_create_permission_calculation_rules_system_not_exist(
        taxi_access_control,
):
    await admin_permission_calculation_rules.create_calculation_rule(
        taxi_access_control,
        'group2',
        'permission-calculation-rule',
        'query',
        'fake-path',
        expected_status_code=404,
        expected_response_json={
            'code': 'system_not_found',
            'message': 'System with name group2 doesn`t exist',
        },
    )

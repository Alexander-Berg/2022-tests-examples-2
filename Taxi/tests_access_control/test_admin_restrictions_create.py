import pytest

from tests_access_control.helpers import admin_restrictions


@pytest.mark.pgsql(
    'access_control', files=['system/group1.sql', 'roles/role1_system1.sql'],
)
async def test_create_restrictions_success(taxi_access_control, pgsql):
    handler_path = '/foo/bar'
    handler_method = 'POST'
    restriction = {
        'init': {
            'arg_name': 'body:sample_int_value',
            'arg_type': 'int',
            'value': 3,
        },
        'type': 'lte',
    }

    await admin_restrictions.create_restriction(
        taxi_access_control,
        system_slug='group1',
        role_slug='role1',
        handler_path=handler_path,
        handler_method=handler_method,
        restriction=restriction,
        expected_status_code=200,
        expected_response_json={
            'restriction': {
                'handler': {'path': handler_path, 'method': handler_method},
                'predicate': restriction,
            },
        },
    )

    cursor = pgsql['access_control'].cursor()
    cursor.execute(
        'SELECT handler_path, handler_method, restriction '
        'FROM access_control.restrictions',
    )

    result = list(cursor)
    assert len(result) == 1, result
    row = result[0]
    assert row[0] == handler_path
    assert row[1] == handler_method
    assert row[2] == restriction


@pytest.mark.pgsql(
    'access_control',
    files=['system/group1.sql', 'roles/role1_system1.sql', 'test_data.sql'],
)
async def test_create_restrictions_conflict_same_restriction(
        taxi_access_control, pgsql,
):
    cursor = pgsql['access_control'].cursor()
    cursor.execute(
        'SELECT handler_path, handler_method, restriction '
        'FROM access_control.restrictions',
    )
    before_handle_call = len(list(cursor))

    await admin_restrictions.create_restriction(
        taxi_access_control,
        system_slug='group1',
        role_slug='role1',
        handler_path='/foo/bar',
        handler_method='POST',
        restriction={},
        expected_status_code=409,
        expected_response_json={
            'code': 'already_exist',
            'message': 'Restriction already exist',
        },
    )

    cursor.execute(
        'SELECT handler_path, handler_method, restriction '
        'FROM access_control.restrictions',
    )
    record_count = len(list(cursor))
    assert record_count == before_handle_call


@pytest.mark.pgsql('access_control', files=['system/group1.sql'])
async def test_create_restrictions_role_not_found(taxi_access_control, pgsql):
    cursor = pgsql['access_control'].cursor()
    cursor.execute(
        'SELECT handler_path, handler_method, restriction '
        'FROM access_control.restrictions',
    )
    before_handle_call = len(list(cursor))

    await admin_restrictions.create_restriction(
        taxi_access_control,
        system_slug='group1',
        role_slug='role1',
        handler_path='/foo/bar',
        handler_method='POST',
        restriction={},
        expected_status_code=404,
        expected_response_json={
            'code': 'role_not_found',
            'message': 'Role "role1" is not found in system "group1"',
        },
    )

    cursor.execute(
        'SELECT handler_path, handler_method, restriction '
        'FROM access_control.restrictions',
    )
    record_count = len(list(cursor))
    assert record_count == before_handle_call

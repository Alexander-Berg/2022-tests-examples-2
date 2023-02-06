import pytest

from hiring_partners_app.stq import hiring_partners_app_users_actions_perform


FIELDS_FOR_TAXIMETER = {
    'park_id',
    'first_name',
    'last_name',
    'phone',
    'license_number',
    'car_brand',
    'car_color',
    'car_model',
    'car_number',
    'hiring_source',
}


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.parametrize('taximeter_response', ['', '1'])
async def test_task(
        _find_user,
        stq3_context,
        mock_partners_taximeter,
        taximeter_response,
        stq,
):
    taximeter = mock_partners_taximeter(taximeter_response)
    login_id = 'YANDEXLOGIN_USER_V1'
    await hiring_partners_app_users_actions_perform.task(
        stq3_context, '1', login_id, 'create_taximeter_account',
    )
    assert taximeter.times_called == 1
    if not taximeter_response:
        assert not stq.is_empty == 1
    else:
        assert stq.is_empty
        user = _find_user(login_id)[0]
        assert user['account_driver_id']
        taximeter_data = taximeter.next_call()['request'].json
        for field in FIELDS_FOR_TAXIMETER:
            assert taximeter_data[field], 'Empty value for field {}'.format(
                field,
            )


@pytest.fixture
def _find_user(pgsql):
    def _wrapper(login_id):
        with pgsql['hiring_partners_app'].cursor() as cursor:
            cursor.execute(
                'SELECT *'
                'FROM "hiring_partners_app"."users"'
                'WHERE "personal_yandex_login_id" = \'{}\''.format(login_id),
            )
            users = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, user)) for user in users]

    return _wrapper

import pytest


FILE_DATA_MARKUP = 'data_markup_response.json'

QUERY = 'SELECT first_name, organization_id FROM hiring_partners_app.users;'


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.parametrize(
    'request_type, case, data_markup',
    [
        ('invalid', 'existing_name', ''),
        ('valid', 'default', ''),
        ('valid', 'activator', ''),
        ('valid', 'org_default', ''),
        ('valid', 'post_process_agent', 'post_process_agent'),
        (
            'invalid',
            'post_process_unknown_action',
            'post_process_unknown_action',
        ),
        (
            'invalid',
            'post_process_disabled_action',
            'post_process_disabled_action',
        ),
        (
            'invalid',
            'post_process_insufficient_fields',
            'post_process_insufficient_fields',
        ),
    ],
)
@pytest.mark.config(HIRING_PARTNERS_APP_ACTIVATORS_ORGANIZATION='0001_1000')
async def test_v1_admin_users_create(
        user_create,
        mock_data_markup_factory,
        load_json,
        request_type,
        case,
        data_markup,
        pgsql,
):
    expected_markup = {}
    if data_markup:
        expected_markup = load_json(FILE_DATA_MARKUP)[data_markup]
    mock_data_markup_factory(expected_markup)
    await user_create(request_type, case)

    if case == 'activator':
        cursor = pgsql['hiring_partners_app'].cursor()
        cursor.execute(QUERY)
        result = list(list(row) for row in cursor)
        assert result[-1][1] == '0001'

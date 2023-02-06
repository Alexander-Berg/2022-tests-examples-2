import pytest

from hiring_partners_app.internal import mass_create_users_from_csv
from hiring_partners_app.internal import organizations_manager

PASTE_FILE = 'paste_responses.json'
FILE_DATA_MARKUP = 'data_markup_response.json'


class Context:
    def __init__(self):
        self.data = 'initial value'

    def set_data(self, data):
        self.data = data


@pytest.fixture
def _paste_context():
    return Context()


@pytest.fixture
def _mock_paste(mockserver, _paste_context):
    class Mocks:
        @mockserver.handler('/download')
        @staticmethod
        async def paste_handler(request):
            return mockserver.make_response(_paste_context.data)

    return Mocks()


@pytest.fixture
def _fetch_table(pgsql):
    async def _fetch(table: str):
        with pgsql['hiring_partners_app'].cursor() as cursor:
            if table == 'organizations':
                cursor.execute(
                    (
                        'SELECT id, external_id, juridical_status, name '
                        'FROM "hiring_partners_app"."{}"'
                    ).format(table),
                )
            else:
                cursor.execute(
                    f'SELECT * FROM "hiring_partners_app"."{table}"',
                )
            raw_events = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, raw_event)) for raw_event in raw_events]

    return _fetch


def _check_result(task, users, organizations, permissions):
    org_id = None
    new_organization = None
    external_id = None
    if task.get('organization'):
        for org in organizations:
            if len(org['id']) == 32:
                org_id = org['id']
                external_id = org['external_id']
                new_organization = org
        assert new_organization
        task['organization']['id'] = org_id
        assert task['organization'] in organizations
    if task.get('users'):
        for _user in users:
            _user.pop('created_at')
            _user.pop('updated_at')
        for user in task['users']:
            if user['organization_id'] == 'NEW_ORG':
                user['organization_id'] = org_id
            assert user in users, f'User: {user}\n\nUSERS:{users}'
    if task.get('permission'):
        task['permission']['organization_id'] = org_id
        task['permission']['title'] = 'New permission for {}'.format(org_id)
        if task['permission']['customer'] is not None:
            task['permission']['customer'] = external_id
        assert task['permission'] in permissions


@pytest.mark.parametrize(
    'case, request_name, error, data_markup',
    [
        ('valid', 'TWO_USERS', None, ''),
        ('valid', 'REQUIRED_FIELDS_ORG_CREATED', None, ''),
        (
            'invalid',
            'MISSING_REQUIRED_FIELDS',
            mass_create_users_from_csv.MissingRequiredFields,
            '',
        ),
        (
            'invalid',
            'MISSING_REQUIRED_VALUES',
            mass_create_users_from_csv.EmptyValue,
            '',
        ),
        (
            'invalid',
            'INVALID_LANGUAGE',
            mass_create_users_from_csv.InvalidValue,
            '',
        ),
        (
            'invalid',
            'INVALID_ENUM',
            mass_create_users_from_csv.InvalidValue,
            '',
        ),
        (
            'invalid',
            'NO_ORG_ID_NO_EXTERNAL_ID',
            organizations_manager.InvalidOrganization,
            '',
        ),
        (
            'invalid',
            'NON_EXISTENT_ORG',
            organizations_manager.InvalidOrganization,
            '',
        ),
        (
            'invalid',
            'DIFFERENT_ORG_ID_EXTERNAL_ID',
            organizations_manager.InvalidOrganization,
            '',
        ),
        (
            'invalid',
            'NEW_ORG_MISSING_FIElDS',
            organizations_manager.InvalidOrganization,
            '',
        ),
        (
            'invalid',
            'NON_EXISTENT_PERMISSION',
            mass_create_users_from_csv.InvalidPermission,
            '',
        ),
        (
            'invalid',
            'DIFFERENT_PERM_EXTERNAL_ID_USER_EXTERNAL_ID',
            mass_create_users_from_csv.InvalidPermission,
            '',
        ),
        ('valid', 'post_process_mass', None, 'post_process_mass'),
        ('valid', 'with_users_and_supervisors', None, ''),
    ],
)
async def test_mass_create_users(
        mock_personal_api,
        mock_data_markup_factory,
        stq,
        _paste_context,
        _mock_paste,
        cron_context,
        load_json,
        _fetch_table,
        case,
        request_name,
        error,
        data_markup,
):
    expected_markup = {}
    if data_markup:
        expected_markup = load_json(FILE_DATA_MARKUP)[data_markup]
    mock_data_markup_factory(expected_markup)
    task = load_json(PASTE_FILE)[case][request_name]
    _paste_context.set_data(task['text'])
    if error:
        valid_error = False
        try:
            await mass_create_users_from_csv.run(
                cron_context, '$mockserver/download',
            )
        except error:
            valid_error = True
        assert valid_error, f'Error must be {error}'
    else:
        await mass_create_users_from_csv.run(
            cron_context, '$mockserver/download',
        )

    users = await _fetch_table('users')
    organizations = await _fetch_table('organizations')
    permissions = await _fetch_table('permissions_groups')
    _check_result(task, users, organizations, permissions)
    if request_name == 'post_process_mass':
        assert not stq.is_empty

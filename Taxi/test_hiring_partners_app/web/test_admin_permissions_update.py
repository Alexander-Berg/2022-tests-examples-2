import pytest


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.parametrize(
    'request_type, case',
    [
        ('valid', 'change_supervisors'),
        ('valid', 'change_users'),
        ('valid', 'change_vacancies'),
        ('valid', 'change_default'),
    ],
)
async def test_v1_admin_permissions_update(
        permissions_create_or_update, request_type, case,
):
    await permissions_create_or_update()
    await permissions_create_or_update(request_type, case, kind='update')

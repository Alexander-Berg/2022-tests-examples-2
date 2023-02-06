import pytest


@pytest.mark.usefixtures('mock_personal_api', 'mock_data_markup')
@pytest.mark.parametrize(
    'request_type, case', [('invalid', 'non_existent'), ('valid', 'default')],
)
async def test_v1_admin_users_update(user_update_admin, request_type, case):
    await user_update_admin(request_type, case)

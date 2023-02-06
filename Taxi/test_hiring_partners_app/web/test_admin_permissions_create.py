import pytest


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.parametrize(
    'request_type, case',
    [('valid', 'default'), ('valid', 'new_default_with_customer')],
)
async def test_v1_admin_permissions_create(
        permissions_create_or_update, request_type, case,
):
    await permissions_create_or_update(request_type, case)

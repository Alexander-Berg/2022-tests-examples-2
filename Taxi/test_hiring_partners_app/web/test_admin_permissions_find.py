import pytest


@pytest.mark.usefixtures('mock_personal_api')
@pytest.mark.parametrize(
    'request_type, case',
    [
        ('valid', 'by_title'),
        ('invalid', 'by_title'),
        ('valid', 'by_id'),
        ('invalid', 'by_id'),
        ('valid', 'by_supervisor'),
        ('invalid', 'by_supervisor'),
        ('valid', 'by_user'),
        ('invalid', 'by_user'),
        ('valid', 'by_org_id'),
        ('invalid', 'by_org_id'),
    ],
)
async def test_v1_admin_permissions_create(
        permissions_create_or_update, request_type, case, permissions_list,
):
    if case not in {'by_customer', 'by_org_id'}:
        await permissions_create_or_update()
    else:
        await permissions_create_or_update(
            'valid', 'new_default_with_customer',
        )
    await permissions_list(request_type, case)

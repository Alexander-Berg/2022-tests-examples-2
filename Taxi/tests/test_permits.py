import pytest

from stall.model.role import PERMITS


def _get_roles_with_permit(permit: str):
    """Возвращает все роли с указанным пермитом"""
    return [r for r, p in PERMITS['roles'].items() if p['permits'].get(permit)]


@pytest.mark.parametrize(
    'permit_truck,permit_trailer',
    (
        ('out_of_company', 'out_of_store'),
        ('store_change_external_id', 'out_of_store'),
        ('stores_seek', 'out_of_store'),
        ('companies_seek', 'out_of_store'),
        ('join_store', 'out_of_store'),
        ('join_company', 'out_of_company'),
        ('courier_shifts_cancel', 'courier_shifts_save'),
    )
)
async def test_related_permits(tap, permit_truck, permit_trailer):
    with tap.plan(1, f'Роли с пермитом "{permit_truck}" обязаны иметь '
                     f'пермит "{permit_trailer}"'):
        trucks = set(_get_roles_with_permit(permit_truck))
        trailers = set(_get_roles_with_permit(permit_trailer))
        tap.eq(trucks - trailers, set(), 'ролей-нарушителей нет')

import pytest

from tests_cargo_crm import const


def get_insert_ticket_sql(
        phone_pd_id=const.PHONE_PD_ID,
        yandex_uid=const.UID,
        ticket_id=const.TICKET_ID,
        is_closed=False,
        is_successful=True,
):
    sql = f"""
    INSERT INTO cargo_crm.tickets (
        phone_pd_id,
        yandex_uid,
        ticket_id,
        is_closed,
        is_successful
    ) VALUES (
        '{phone_pd_id}',
        '{yandex_uid}',
        '{ticket_id}',
        {is_closed},
        {is_successful}
    )"""

    return sql


TICKETS = [
    dict(
        yandex_uid=const.UID,
        is_successful=True,
        is_closed=False,
        ticket_id=const.TICKET_ID,
    ),
    dict(
        yandex_uid=const.UID,
        is_successful=False,
        is_closed=True,
        ticket_id=const.ANOTHER_TICKET_ID,
    ),
]


@pytest.mark.pgsql(
    'cargo_crm',
    queries=[get_insert_ticket_sql(**ticket) for ticket in TICKETS],
)
@pytest.mark.parametrize(
    'filtered_phone, expected_tickets',
    (
        pytest.param(const.PHONE, TICKETS[::-1], id='ok not empty'),
        # pytest.param(const.ANOTHER_PHONE, [], id='ok but empty'),  # flapy
    ),
)
async def test_admin_phoenix_state(
        taxi_cargo_crm,
        personal_ctx,
        personal_handler_find,
        filtered_phone,
        expected_tickets,
):
    personal_ctx.set_phones([{'id': const.PHONE_PD_ID, 'value': const.PHONE}])
    response = await taxi_cargo_crm.post(
        '/admin/cargo-crm/flow/phoenix/state',
        json={'chosen_phone': filtered_phone},
        headers={'X-Yandex-Uid': const.ANOTHER_UID},
    )
    assert response.status_code == 200
    assert response.json() == {
        'all_registered_companies': [],
        'all_tickets': expected_tickets,
    }

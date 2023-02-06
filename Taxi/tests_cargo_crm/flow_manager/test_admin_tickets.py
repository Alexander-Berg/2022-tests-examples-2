import pytest

from tests_cargo_crm import utils

RANGE = {'older_than_ts': '2020-10-10T10:00:00+03:00', 'results': 10}

FILTER_0 = {
    'only_opened': True,
    'country': 'isr',
    'company_name': 'Retrograde Mercury',
    'step_passed': 'curator_action',
    'step_expected': 'curator_action_received',
}

FILTER_1 = {'country': 'rus', 'step_passed': 'curator_action'}

TICKET_0 = {
    'company_inn': '4302245589',
    'company_name': 'retrograde mercury',
    'country': 'isr',
    'created_ts': '2020-09-10T07:00:00+00:00',
    'is_closed': False,
    'is_successful': True,
    'step_expected': 'curator_action_received',
    'step_passed': 'curator_action',
    'ticket_id': 'ticket_id670089',
    'updated_ts': '2020-09-10T07:00:00+00:00',
}

TICKET_1 = {
    'company_inn': '4302245589',
    'company_name': 'Retrograde Mercury',
    'country': 'isr',
    'created_ts': '2019-10-10T07:00:00+00:00',
    'is_closed': False,
    'is_successful': True,
    'step_expected': 'curator_action_received',
    'step_passed': 'curator_action',
    'ticket_id': 'ticket_id540911',
    'updated_ts': '2019-12-10T07:00:00+00:00',
}

TICKET_2 = {
    'ticket_id': 'ticket_id540876',
    'created_ts': '2019-10-10T07:00:00+00:00',
    'updated_ts': '2019-10-10T07:00:00+00:00',
    'country': 'rus',
    'company_name': 'Retrograde Mercury',
    'company_inn': '4302245589',
    'step_passed': 'curator_action',
    'step_expected': 'curator_action_received',
    'is_closed': False,
    'is_successful': True,
}


def _prepare_tickets(pgsql):
    utils.create_ticket(
        pgsql,
        'ticket_id540911',
        '2019-10-10T10:00:00+03:00',
        '2019-12-10T10:00:00+03:00',
        'isr',
        'Retrograde Mercury',
        '4302245589',
        step_passed='curator_action',
        step_expected='curator_action_received',
        is_closed=False,
    )

    utils.create_ticket(
        pgsql,
        'ticket_id670089',
        '2020-09-10T10:00:00+03:00',
        '2020-09-10T10:00:00+03:00',
        'isr',
        'retrograde mercury',
        '4302245589',
        step_passed='curator_action',
        step_expected='curator_action_received',
        is_closed=False,
    )

    utils.create_ticket(
        pgsql,
        'ticket_id540876',
        '2019-10-10T10:00:00+03:00',
        '2019-10-10T10:00:00+03:00',
        'rus',
        'Retrograde Mercury',
        '4302245589',
        step_passed='curator_action',
        step_expected='curator_action_received',
        is_closed=False,
    )

    utils.create_ticket(
        pgsql,
        'ticket_id540401',
        '2021-10-10T10:00:00+03:00',
        '2021-10-10T10:00:00+03:00',
        'isr',
        'Retrograde Mercury',
        '4302245589',
        step_passed='curator_action',
        step_expected='curator_action_received',
        is_closed=False,
    )

    utils.create_ticket(
        pgsql,
        'ticket_id540907',
        '2019-10-10T10:00:00+03:00',
        '2019-12-10T10:00:00+03:00',
        'isr',
        'Retrograde Mercury',
        '4302245589',
        step_passed='curator_action',
        step_expected='curator_action_received',
        is_closed=True,
    )

    utils.create_ticket(
        pgsql,
        'ticket_id779011',
        '2016-10-10T10:00:00+03:00',
        '2018-12-10T10:00:00+03:00',
        'isr',
        'Retrograde Mercury',
        '4302245589',
        step_passed='initial_form_received',
        step_expected='autocheck_passed',
        is_closed=False,
    )


@pytest.mark.parametrize(
    'request_filter,expected_tickets',
    [(FILTER_0, [TICKET_0, TICKET_1]), (FILTER_1, [TICKET_2])],
)
async def test_admin_manager_tickets(
        pgsql, taxi_cargo_crm, request_filter, expected_tickets,
):
    _prepare_tickets(pgsql)

    response = await taxi_cargo_crm.post(
        '/admin/cargo-crm/flow/manager/tickets',
        headers={
            'Accept-Language': 'ru',
            'X-Yandex-Uid': utils.YANDEX_UID,
            'X-Yandex-Login': utils.YANDEX_LOGIN,
        },
        json={'range': RANGE, 'filter': request_filter},
    )
    assert response.status_code == 200
    assert response.json()['tickets'] == expected_tickets

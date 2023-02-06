import pytest

from tests_cargo_crm import const

CARGO_CORP_COUNTRY_SPECIFICS = {
    'rus': {
        'email_slugs': {'autogen_credentials': 'autogen_credentials_slug'},
    },
}

ENCRYPTED_PASSWORD = 'pVLgvCMH6Rmx17dOLxmRASArsO5BLpX5MP6419HWB5E='


def get_task_kwargs():
    return {
        'email_pd_id': 'Vice.Inc@yandex.ru_id',
        'yandex_login_pd_id': 'yandex_login_pd_id',
        'encrypted_temp_password': ENCRYPTED_PASSWORD,
        'country': 'rus',
    }


@pytest.mark.config(CARGO_CORP_COUNTRY_SPECIFICS=CARGO_CORP_COUNTRY_SPECIFICS)
async def test_stq_send_autogen_credentials(
        stq_runner, stq, personal_mocks, sender_mocks,
):
    sender_mocks.send_autogen_credentials_slug.set_expected_data(
        {
            'args': {'login': 'yandex_login_pd', 'password': 'sword'},
            'to': [{'email': 'Vice.Inc@yandex.ru'}],
        },
    )
    sender_mocks.send_autogen_credentials_slug.set_response(
        200, {'result': {'status': 'ok', 'task_id': '1', 'message_id': '1'}},
    )

    await stq_runner.cargo_crm_send_autogen_credentials.call(
        task_id=const.TICKET_ID, kwargs=get_task_kwargs(),
    )

    assert sender_mocks.send_autogen_credentials_slug_times_called == 1


async def test_handler_send_autogen_credentials(
        pgsql, taxi_cargo_crm, stq, personal_mocks, sender_mocks,
):
    cursor = pgsql['cargo_crm'].cursor()
    cursor.execute(
        'INSERT INTO cargo_crm_manager.tickets_data('
        'ticket_id,ticket_data)'
        'VALUES(\'{}\',\'{}\') '
        ''.format(
            const.TICKET_ID,
            f"""{{"company_info_pd_form": {{ "email_pd_id": "Vice.Inc@yandex.ru_id" }},
            "company_info_form": {{"name": "_", "country": "_" }},
            "offer_info_form": {{ 
                "name": "_",  "longname": "_", "postcode": "362013", 
                "postaddress": "_",  "legaladdress": "_", "kind": "rus", 
                "country": "rus",  "inn": "879571636629", "bik": "044525225", 
                "account": "40703810938000010045"
            }},
            "contract_traits_form": {{ "kind": "_", "payment_type": "postpaid" }},
            "manager_info_form": {{ "manager": {{ "login": "_" }} }} }}""",
        ),
    )
    cursor.close()

    sender_mocks.send_autogen_credentials_slug.set_expected_data(
        {
            'args': {'login': 'yandex_login_pd', 'password': 'sword'},
            'to': [{'email': 'Vice.Inc@yandex.ru'}],
        },
    )
    sender_mocks.send_autogen_credentials_slug.set_response(
        200, {'result': {'status': 'ok', 'task_id': '1', 'message_id': '1'}},
    )

    response = await taxi_cargo_crm.post(
        '/internal/cargo-crm/flow/manager/ticket/send-autogen-credentials?ticket_id='
        + const.TICKET_ID,
        json={
            'yandex_login_pd_id': 'yandex_login_pd_id',
            'encrypted_temp_password': ENCRYPTED_PASSWORD,
            'country': 'rus',
        },
    )

    assert response.status == 200
    assert stq.cargo_crm_send_autogen_credentials.times_called == 1

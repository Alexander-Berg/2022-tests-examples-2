YANDEX_UID = 'yandex_uid1'
YANDEX_LOGIN = 'yandex_login1'


def create_ticket(
        pgsql,
        ticket_id,
        created_ts,
        updated_ts,
        country,
        company_name,
        company_inn,
        step_passed,
        step_expected,
        is_closed=False,
        is_successful=True,
):
    cursor = pgsql['cargo_crm'].conn.cursor()
    cursor.execute(
        'INSERT INTO cargo_crm_manager.tickets('
        'ticket_id,created_ts,updated_ts,'
        'country,company_name,company_inn,'
        'step_passed,step_expected,'
        'is_closed,is_successful)'
        'VALUES(\'{}\',\'{}\',\'{}\',\'{}\','
        '\'{}\',\'{}\',\'{}\',\'{}\',{},{}) '
        ''.format(
            ticket_id,
            created_ts,
            updated_ts,
            country,
            company_name,
            company_inn,
            step_passed,
            step_expected,
            is_closed,
            is_successful,
        ),
    )

    cursor.close()

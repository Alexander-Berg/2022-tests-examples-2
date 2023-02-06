import datetime
import unittest
import uuid

CARD_ID = 'cardstorage_card_id'
CORP_CLIENT_ID = 'corp_client_id_1_______32symbols'
CORP_CLIENT_ID_1 = 'corp_client_id_12345678910111213'
CORP_CLIENT_ID_2 = 'corp_client_id_12345678910111214'
CORP_CLIENT_NAME = 'corp_client_name'
EXTERNAL_REF_FMT = 'corp:{}:api'
INTERNAL_PREFIX = '/internal/cargo-corp'
YANDEX_UID = 'yandex_uid1'
YANDEX_LOGIN = 'yandex_login1'
YANDEX_LOGIN_PD_ID = 'yandex_login1_id'
YANDEX_EMAIL = 'yandex_login1@ya.ru'
YANDEX_EMAIL_PD_ID = 'yandex_login1@ya.ru_id'
EMPLOYEE_NAME = 'employee_name'
ROBOT_TOKEN = '12345'
PHONE = '87776667766'
PHONE_PD_ID = '87776667766_id'
ROLE_ID = 'default_role_id'
OWNER_ROLE = 'system:owner'
OWNER_ROLE_TRANSLATION = 'Owner'
NON_GENERAL_ROLE_ID = 'role_id'
NON_GENERAL_ROLE_NAME = 'role_name'
BAD_RESPONSE = {'code': 'error', 'message': 'Error'}
BILLING_ID = '123456789'
PERSON_ID = '1234567'
PHOENIX_CONTRACT = {
    'id': '12345',
    'external_id': '123/45',
    'kind': 'offer',
    'payment_type': 'prepaid',
}

CORP_CLIENT_INFO = {
    'corp_client_id': CORP_CLIENT_ID,
    'company': {'name': 'test_company_name', 'country': 'rus'},
    'revision': 1,
    'created_ts': '2021-05-31T19:00:00+00:00',
    'updated_ts': '2021-05-31T19:00:00+00:00',
}

ALL_PERMISSION_IDS = [
    {'id': perm}
    for perm in (
        'corp_client',
        'claims_view',
        'claims_edit',
        'staff_view',
        'staff_edit',
        'paydata_view',
        'paydata_edit',
    )
]

SOME_PERMISSION_IDS = ALL_PERMISSION_IDS[-2:]

PASSPORT_ACCOUNT = {
    'name': 'Super',
    'surname': 'Scooter',
    'phones': [
        {'phone': '+79001234000', 'need_confirmation': False},
        {'phone': '+79009876000', 'need_confirmation': True},
    ],
}

CARD_ID = 'card_1'


def _prepare_optional_string(value, with_equal_condition=False):
    if with_equal_condition:
        return f' = \'{value}\'' if value else ' IS NULL'
    return f'\'{value}\'' if value else 'NULL'


def _get_ids_set(permissions):
    return set(permission['id'] for permission in permissions)


def assert_ids_are_equal(ids_first, ids_second):
    assert _get_ids_set(ids_first) == _get_ids_set(ids_second)


def assert_items_equal(result, expected):
    """
    Result and expected have the same elements in the same number,
    regardless of their order
    """

    case = unittest.TestCase()
    case.maxDiff = None
    case.assertCountEqual(result, expected)


def assert_increased_updated_ts(result: dict, expected: dict):
    """
    Asserts two dicts where result has increased updated_ts
    """

    assert (
        result['updated_ts'] > expected['updated_ts']
    ), f'{result["updated_ts"]} > {expected["updated_ts"]}'

    new_updated_ts = result['updated_ts']
    result['updated_ts'] = expected['updated_ts']

    assert result == expected
    result['updated_ts'] = new_updated_ts


def get_client_create_request(
        corp_client_id=CORP_CLIENT_ID,
        corp_client_name=CORP_CLIENT_NAME,
        sharded_key_hash='12345',
        is_removed=False,
        country='rus',
        is_registered=False,
):
    return (
        """
        INSERT INTO corp_clients.clients(
            corp_client_id,
            name,
            sharded_key_hash,
            is_removed,
            country,
            registration_finished_ts
        ) VALUES (
            '{}',
            '{}',
            {},
            {},
            '{}',
            {}
        )
        ON CONFLICT (corp_client_id)
        DO NOTHING
    """.format(
            corp_client_id,
            corp_client_name,
            sharded_key_hash,
            is_removed,
            country,
            _prepare_optional_string(
                datetime.datetime.utcnow() if is_registered else None,
            ),
        )
    )


def get_candidate_create_request(
        corp_client_id=CORP_CLIENT_ID,
        confirmation_code='test_confirmation_code',
        name='test_candidate_name',
        phone_pd_id='1234567890_id',
        role_id=ROLE_ID,
        email_pd_id='test@ya.ru',
        revision=1,
):
    return (
        """
        INSERT INTO corp_clients.employee_candidates (
            corp_client_id,
            confirmation_code,
            name,
            phone_pd_id,
            role_id,
            email_pd_id,
            revision
        ) VALUES (
            \'{0}\',
            \'{1}\',
            \'{2}\',
            \'{3}\',
            \'{4}\',
            \'{5}\',
            \'{6}\'
        )
        ON CONFLICT DO NOTHING
        RETURNING
            corp_client_id,
            confirmation_code,
            name,
            phone_pd_id,
            role_id,
            email_pd_id,
            revision
        """.format(
            corp_client_id,
            confirmation_code,
            name,
            phone_pd_id,
            role_id,
            email_pd_id,
            revision,
        )
    )


def get_role_create_request(
        is_removable=True,
        permission_ids=ALL_PERMISSION_IDS,
        role_name=OWNER_ROLE,
        is_removed=False,
        corp_client_id=CORP_CLIENT_ID,
        role_id=None,
):
    if not role_id:
        role_id = str(uuid.uuid4())
    return (
        """
        INSERT INTO corp_clients.client_roles(
        id, corp_client_id,role_name,permissions,is_removable,is_removed)
        VALUES(\'{}\', {},\'{}\',ARRAY[\'{}\'],{},{})
        ON CONFLICT (corp_client_id,role_name)
        DO UPDATE SET
            permissions = EXCLUDED.permissions,
            is_removable = EXCLUDED.is_removable,
            is_removed = EXCLUDED.is_removed
        RETURNING id
        """.format(
            role_id,
            _prepare_optional_string(corp_client_id),
            role_name,
            '\',\''.join(_get_ids_set(permission_ids)),
            is_removable,
            is_removed,
        )
    )


def create_client(
        pgsql,
        corp_client_id=CORP_CLIENT_ID,
        corp_client_name=CORP_CLIENT_NAME,
        is_removed=False,
        country='rus',
        is_registered=False,
):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        get_client_create_request(
            corp_client_id,
            corp_client_name,
            '12345',
            is_removed,
            country,
            is_registered,
        ),
    )

    cursor.close()


def create_role(
        pgsql,
        is_removable=True,
        permission_ids=ALL_PERMISSION_IDS,
        role_name=OWNER_ROLE,
        is_removed=False,
        corp_client_id=CORP_CLIENT_ID,
        role_id=None,
):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        get_role_create_request(
            is_removable,
            permission_ids,
            role_name,
            is_removed,
            corp_client_id,
            role_id,
        ),
    )
    row = cursor.fetchone()
    cursor.close()

    role_id = row[0]
    return role_id


def create_employee(
        pgsql,
        corp_client_id=CORP_CLIENT_ID,
        yandex_uid=YANDEX_UID,
        phone_pd_id=PHONE_PD_ID,
        yandex_login_pd_id=YANDEX_LOGIN_PD_ID,
        email_pd_id=YANDEX_EMAIL_PD_ID,
        name=EMPLOYEE_NAME,
        is_disabled=False,
        is_removed=False,
        is_robot=False,
):
    robot_external_ref = (
        EXTERNAL_REF_FMT.format(corp_client_id) if is_robot else None
    )

    with pgsql['cargo_corp'].dict_cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO corp_clients.employees(
            corp_client_id,yandex_uid,phone_pd_ids,
            name,is_disabled,is_removed,robot_external_ref,
            yandex_login_pd_id, email_pd_id)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (corp_client_id,yandex_uid) DO NOTHING
            """,
            (
                corp_client_id,
                yandex_uid,
                [phone_pd_id],
                name,
                is_disabled,
                is_removed,
                robot_external_ref,
                yandex_login_pd_id,
                email_pd_id,
            ),
        )


def register_employee(
        pgsql,
        corp_client_id=CORP_CLIENT_ID,
        yandex_uid=YANDEX_UID,
        phone_pd_id=PHONE_PD_ID,
        key_hash=3755605199,
):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        'INSERT INTO corp_employees.clients('
        'corp_client_id,yandex_uid,sharded_key_hash) '
        'VALUES(\'{}\',\'{}\',{}) '
        'ON CONFLICT (corp_client_id,yandex_uid) DO NOTHING '
        ''.format(corp_client_id, yandex_uid, key_hash),
    )
    cursor.execute(
        'INSERT INTO employees_phone_pd_ids.employees('
        'phone_pd_id,sharded_key_hash,yandex_uid,corp_client_id) '
        'VALUES(\'{}\',{},\'{}\',\'{}\') '
        'ON CONFLICT (corp_client_id,yandex_uid) DO NOTHING '
        ''.format(phone_pd_id, key_hash, yandex_uid, corp_client_id),
    )

    cursor.close()


def add_card(
        pgsql,
        corp_client_id=CORP_CLIENT_ID,
        yandex_uid=YANDEX_UID,
        card_id=CARD_ID,
):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        'INSERT INTO corp_clients.bound_cards('
        'corp_client_id,yandex_uid,card_id,is_bound) '
        'VALUES(\'{}\',\'{}\',\'{}\',TRUE) '
        'ON CONFLICT (corp_client_id,yandex_uid,card_id) '
        'DO NOTHING '.format(corp_client_id, yandex_uid, card_id),
    )

    cursor.close()


def create_employee_role(
        pgsql,
        role_id,
        corp_client_id=CORP_CLIENT_ID,
        yandex_uid=YANDEX_UID,
        is_removed=False,
):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        'INSERT INTO corp_clients.employee_roles('
        'corp_client_id,yandex_uid,role_id,is_removed) '
        'VALUES(\'{}\',\'{}\',\'{}\',{}) '.format(
            corp_client_id, yandex_uid, role_id, is_removed,
        ),
    )

    cursor.close()


def create_employee_with_perms(
        pgsql,
        yandex_uid=YANDEX_UID,
        role_name=OWNER_ROLE,
        permission_ids=ALL_PERMISSION_IDS,
        is_general_role=True,
):
    role_id = create_role(
        pgsql,
        role_name=role_name,
        permission_ids=permission_ids,
        corp_client_id=None if is_general_role else CORP_CLIENT_ID,
    )
    create_employee(pgsql, yandex_uid=yandex_uid)
    create_employee_role(pgsql, role_id, yandex_uid=yandex_uid)


def get_role_info_by_name(pgsql, role_name, corp_client_id=None):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        'SELECT id, revision '
        'FROM corp_clients.client_roles '
        'WHERE corp_client_id {} '
        'AND role_name = \'{}\' '.format(
            _prepare_optional_string(
                corp_client_id, with_equal_condition=True,
            ),
            role_name,
        ),
    )
    rows = cursor.fetchall()
    cursor.close()

    role_id = rows[0][0] if rows else None
    revision = rows[0][1] if rows else None

    return role_id, revision


def get_employees_by_role(pgsql, role_id):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        'SELECT yandex_uid '
        'FROM corp_clients_views.employee_roles '
        'WHERE role_id = \'{}\' '.format(role_id),
    )
    rows = cursor.fetchall()
    cursor.close()

    return [row[0] for row in rows]


def get_employees(pgsql):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        'SELECT yandex_uid '
        'FROM corp_clients_views.employees '
        'WHERE corp_client_id = \'{}\' '.format(CORP_CLIENT_ID),
    )
    rows = cursor.fetchall()
    cursor.close()

    return [row[0] for row in rows]


def get_roles(pgsql):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        'SELECT id '
        'FROM corp_clients_views.client_roles '
        'WHERE corp_client_id = \'{}\' '.format(CORP_CLIENT_ID),
    )
    rows = cursor.fetchall()
    cursor.close()

    return [row[0] for row in rows]


def create_employee_candidate(
        pgsql,
        confirmation_code='test_confirmation_code',
        name='test_candidate_name',
        corp_client_id=CORP_CLIENT_ID,
        phone_pd_id='1234567890_id',
        role_id=ROLE_ID,
        email_pd_id='test@ya.ru',
        revision=1,
):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        get_candidate_create_request(
            corp_client_id,
            confirmation_code,
            name,
            phone_pd_id,
            role_id,
            email_pd_id,
            revision,
        ),
    )

    row = cursor.fetchone()
    cursor.close()

    return row


def get_employee_candidate_info(
        pgqsql,
        confirmation_code='test_confirmation_code',
        corp_client_id=CORP_CLIENT_ID,
):
    cursor = pgqsql['cargo_corp'].conn.cursor()

    cursor.execute(
        """
        SELECT
            ec.confirmation_code,
            ec.name,
            ec.phone_pd_id,
            ec.role_id,
            ec.email_pd_id,
            cr.role_name,
            ec.revision,
            c.name AS corp_client_name
        FROM corp_clients.employee_candidates as ec
        INNER JOIN corp_clients.clients AS c
            USING (corp_client_id)
        LEFT JOIN corp_clients_views.client_roles as cr
            ON cr.id = ec.role_id
        WHERE
            ec.corp_client_id = \'{}\'
            AND
            ec.confirmation_code = \'{}\'
        """.format(
            corp_client_id, confirmation_code,
        ),
    )

    row = cursor.fetchone()
    cursor.close()
    if not row:
        return {}
    return {
        'confirmation_code': row[0],
        'revision': row[6],
        'corp_client_name': row[7],
        'info': {
            'name': row[1],
            'phone': {'number': row[2][:-3]},
            'role_id': row[3],
            'email': row[4],
            'role_name': row[5],
        },
    }


def get_client_by_id(pgsql, corp_client_id):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        """
        SELECT
            corp_client_id,
            registration_finished_ts::TEXT
        FROM corp_clients.clients
            WHERE corp_client_id = \'{}\'
    """.format(
            corp_client_id,
        ),
    )
    rows = cursor.fetchone()
    cursor.close()

    return rows


def remove_role(pgsql, role_id):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        """
        UPDATE corp_clients.client_roles
        SET
            is_removed = TRUE
        WHERE
            id = \'{}\'
            AND
            NOT is_removed
            AND
            is_removable
        RETURNING
            id,
            corp_client_id,
            role_name,
            permissions,
            revision
    """.format(
            role_id,
        ),
    )
    row = cursor.fetchone()
    cursor.close()

    return row


def get_client_extra_info(pgsql, corp_client_id):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        """
        SELECT
            extra_info,
            extra_info_tag
        FROM corp_clients.client_extra_info
        WHERE
            corp_client_id = \'{0}\'
    """.format(
            corp_client_id,
        ),
    )
    row = cursor.fetchone()
    cursor.close()

    return row


def get_client_balance_info(pgsql, corp_client_id):
    cursor = pgsql['cargo_corp'].conn.cursor()

    cursor.execute(
        """
        SELECT
            billing_id,
            person_id,
            contract_id,
            contract_eid,
            contract_type,
            payment_type
        FROM corp_clients.balance_info
        WHERE
            corp_client_id = \'{0}\'
    """.format(
            corp_client_id,
        ),
    )
    row = cursor.fetchone()
    cursor.close()

    return row

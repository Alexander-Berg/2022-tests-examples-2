import json

TEST_PAYMENT_ID = 'd9abbfb7-84d4-44be-94b3-8f8ea7eb31df'
TEST_WALLET_ID = 'test_wallet_id_123456'
APPLICATION_ID_PROCESSING = '7948e3a9-623c-4524-a390-9e4264d27a00'
APPLICATION_ID_FAILED = '7948e3a9-623c-4524-a390-9e4264d27a01'
APPLICATION_ID_SUCCESS = '7948e3a9-623c-4524-a390-9e4264d27a02'
APPLICATION_ID_CREATED = '7948e3a9-623c-4524-a390-9e4264d27a03'
APPLICATION_ID_NOEXIST = '7948e3a9-623c-4524-a390-9e4264d27a04'

DEFAULT_YABANK_SESSION_UUID = 'session_uuid_1'
DEFAULT_YABANK_PHONE_ID = 'phone_id_1'
DEFAULT_YANDEX_BUID = 'bank_uid'
DEFAULT_YANDEX_UID = 'uid_1'
DEFAULT_USER_TICKET = 'user_ticket_1'
DEFAULT_CARD_ID = '11111111-63aa-4838-9ec7-111111111111'
DEFAULT_AGREEMENT_ID = 'agreement_id_1'
DEFAULT_PUBLIC_AGREEMENT_ID = 'public_agreement_id_1'
DEFAULT_PHONE = '+70001002020'
DEFAULT_PAYMENT_METHOD_ID = 'trust_payment_id_1'
DEFAULT_IDEMPOTENCY_TOKEN = 'ffffffff-ffff-ffff-ffff-111111111111'
DEFAULT_EXECUTE_IDEMPOTENCY_TOKEN = 'eeeeeeee-eeee-eeee-eeee-111111111111'

DEFAULT_AUTOTOPUP_ID = 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa'
DEFAULT_AUTOTOPUP_INTERNAL_ID = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
DEFAULT_WATCHDOG_ID = 'cccccccc-cccc-cccc-cccc-cccccccccccc'
DEFAULT_CURRENCY = 'RUB'
DEFAULT_CURRENCY_SIGN = '₽'
DEFAULT_AMOUNT = '100'
DEFAULT_MONEY = {'amount': DEFAULT_AMOUNT, 'currency': DEFAULT_CURRENCY}
DEFAULT_THRESHOLD = {'amount': DEFAULT_AMOUNT, 'currency': DEFAULT_CURRENCY}
DEFAULT_AUTOTOPUP_TYPE = 'LIMIT_EXACT'

ANOTHER_YANDEX_BUID = 'buid_2'
ANOTHER_IDEMPOTENCY_TOKEN = 'ffffffff-ffff-ffff-ffff-222222222222'
ANOTHER_PUBLIC_AGREEMENT_ID = 'public_agreement_id_2'
ANOTHER_METHOD_PAYMENT_ID = 'trust_payment_id_2'
ANOTHER_WATCHDOG_ID = 'cccccccc-cccc-cccc-cccc-dddddddddddd'
ANOTHER_AMOUNT = '1000'

V1_HANDLE_PATH = '/v1/topup/v1/get_topup_info'
V2_HANDLE_PATH = '/v1/topup/v2/get_topup_info'

TRUST_BASKET_INFO = {
    'purchase_token': 'purchase_token',
    'amount': '100',
    'currency': 'RUB',
    'payment_status': 'not_started',
    'payment_timeout': '1200.00',
    'start_ts': '1630656576.841',
    'final_status_ts': '1630656600.841',
    'paymethod_id': 'card-xc153df956eadfc0868925ed6',
    'payment_method': 'card',
    'user_account': '444433****1111',
    'card_type': 'VISA',
    'orders': [{'order_id': '165469887', 'order_ts': '1630656576.123'}],
}


def get_default_headers():
    return {
        'X-Yandex-BUID': '1',
        'X-YaBank-SessionUUID': '1',
        'X-Yandex-UID': '1',
        'X-YaBank-PhoneID': '1',
        'X-Request-Language': 'ru',
        'X-Ya-User-Ticket': '1',
        'X-YaBank-ColorTheme': 'LIGHT',
    }


def get_support_headers():
    return {'X-Bank-Token': 'allow'}


def get_payment_status(pgsql, payment_id=TEST_PAYMENT_ID):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'select status '
        'from bank_topup.payments '
        'where payment_id = %s::UUID',
        (payment_id,),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert len(rows[0]) == 1
    return rows[0][0]


def get_trust_payment_id(pgsql, payment_id=TEST_PAYMENT_ID):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'select trust_payment_id '
        'from bank_topup.payments '
        'where payment_id = %s::UUID',
        (payment_id,),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert len(rows[0]) == 1
    return rows[0][0]


def get_payment_info(pgsql, payment_id=TEST_PAYMENT_ID):
    cursor = pgsql['bank_topup'].cursor()
    db_fields = [
        'payment_id',
        'bank_uid',
        'yandex_uid',
        'idempotency_token',
        'status',
        'amount',
        'currency',
        'wallet_id',
        'session_uuid',
        'client_ip',
        'public_agreement_id',
    ]
    cursor.execute(
        f'select {",".join(db_fields)} '
        f'from bank_topup.payments '
        f'where payment_id = \'{payment_id}\'::UUID',
        (payment_id,),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    return dict(zip(db_fields, rows[0]))


def set_payment_status(pgsql, payment_id=TEST_PAYMENT_ID, status='CREATED'):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'update bank_topup.payments '
        'set status = %s '
        'where payment_id = %s::UUID',
        (status, payment_id),
    )


def set_payment_currency(
        pgsql, payment_id=TEST_PAYMENT_ID, currency=DEFAULT_CURRENCY,
):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'update bank_topup.payments '
        'set currency = %s '
        'where payment_id = %s::UUID',
        (currency, payment_id),
    )


def set_payment_amount(
        pgsql, payment_id=TEST_PAYMENT_ID, amount=DEFAULT_AMOUNT,
):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'update bank_topup.payments '
        'set amount = %s '
        'where payment_id = %s::UUID',
        (amount, payment_id),
    )


def set_card_info(
        pgsql,
        payment_system,
        card_bin,
        last_digits,
        payment_id=TEST_PAYMENT_ID,
):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        f'update bank_topup.payments '
        f'set card_payment_system '
        f'= \'{payment_system}\'::bank_topup.payment_system, '
        f'card_bin = \'{card_bin}\', '
        f'card_last_digits = \'{last_digits}\' '
        f'where payment_id = \'{payment_id}\'::UUID',
    )


def set_rrn(pgsql, payment_id=TEST_PAYMENT_ID, rrn=None):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'UPDATE bank_topup.payments '
        'SET rrn = %s '
        'WHERE payment_id = %s::UUID',
        (rrn, payment_id),
    )


def get_exceed_limit_widget_theme(need_image=True):
    widget = {
        'background': {'color': 'FFFFF0E0'},
        'title_text_color': 'FFA15912',
        'description_text_color': 'FFA15912',
        'delimiter_color': 'FF98591B',
        'button_theme': {
            'background': {'color': 'FFFFF0E0'},
            'text_color': 'FFA15912',
        },
    }
    if need_image:
        widget['image'] = {
            'size_type': 'TITLE',
            'url': (
                'https://avatars.mdst.yandex.net/get-fintech/0000000/limit_png'
            ),
        }
    return widget


def make_checks(
        bank_core_statement_mock,
        expected_response,
        response,
        status_code: int = 200,
        handle_path=V1_HANDLE_PATH,
):
    assert response.status_code == status_code
    if handle_path == V1_HANDLE_PATH:
        assert bank_core_statement_mock.wallets_balance_handler.has_calls
    elif handle_path == V2_HANDLE_PATH:
        assert bank_core_statement_mock.agreements_balance_handler.has_calls
    assert response.json() == expected_response


def make_body(handle_path, balance_id, application_id=None):
    body = {}
    if application_id:
        body.update({'application_id': application_id})

    if handle_path == V1_HANDLE_PATH:
        body.update({'wallet_id': balance_id})
    elif handle_path == V2_HANDLE_PATH:
        body.update({'agreement_id': balance_id})
    return body


def extend_expected_result(result, handle_path):
    if handle_path == V1_HANDLE_PATH:
        result.update({'yandex_uid': '1'})
    return result


def set_wallet_id(pgsql, payment_id=TEST_PAYMENT_ID, wallet_id=TEST_WALLET_ID):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'update bank_topup.payments '
        'set wallet_id = %s '
        'where payment_id = %s::UUID',
        (wallet_id, payment_id),
    )


def set_agreement_id(
        pgsql,
        payment_id=TEST_PAYMENT_ID,
        public_agreement_id=DEFAULT_PUBLIC_AGREEMENT_ID,
        wallet_id=None,
):
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        'update bank_topup.payments '
        'set public_agreement_id = %s,  wallet_id = %s '
        'where payment_id = %s::UUID',
        (public_agreement_id, wallet_id, payment_id),
    )


def get_pending_payments_status(payments):
    actual_payments = []
    for payment in payments:
        actual_payments.append(
            [payment['payment_info']['payment_id'], payment['status']],
        )
    return actual_payments


def get_autotopup(pgsql, autotopup_id):
    cursor = pgsql['bank_topup'].cursor()
    db_fields = [
        'autotopup_id',
        'bank_uid',
        'yandex_uid',
        'idempotency_token',
        'autotopup_internal_id',
        'type',
        'enabled',
        'params',
        'enabled_at',
        'disabled_at',
        'cursor_key',
    ]
    cursor.execute(
        f'select {",".join(db_fields)} '
        f'from bank_topup.autotopups '
        f'where autotopup_id = \'{autotopup_id}\'::UUID',
        (autotopup_id,),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    return dict(zip(db_fields, rows[0]))


def make_autotopup(
        bank_uid=DEFAULT_YANDEX_BUID,
        yandex_uid=DEFAULT_YANDEX_UID,
        idempotency_token=DEFAULT_IDEMPOTENCY_TOKEN,
        autotopup_internal_id=DEFAULT_AUTOTOPUP_INTERNAL_ID,
        autotopup_id=DEFAULT_AUTOTOPUP_ID,
        autotopup_type=DEFAULT_AUTOTOPUP_TYPE,
        enabled=True,
        public_agreement_id=DEFAULT_PUBLIC_AGREEMENT_ID,
        payment_method_id=DEFAULT_PAYMENT_METHOD_ID,
        currency=DEFAULT_CURRENCY,
        money_amount=DEFAULT_AMOUNT,
        threshold_amount=DEFAULT_AMOUNT,
        enabled_at=None,
        disabled_at=None,
        cursor_key=None,
):
    return {
        'bank_uid': bank_uid,
        'yandex_uid': yandex_uid,
        'idempotency_token': idempotency_token,
        'autotopup_id': autotopup_id,
        'autotopup_internal_id': autotopup_internal_id,
        'type': autotopup_type,
        'enabled': enabled,
        'params': {
            'public_agreement_id': public_agreement_id,
            'payment_method_id': payment_method_id,
            'currency': currency,
            'money_amount': money_amount,
            'threshold_amount': threshold_amount,
        },
        'enabled_at': enabled_at,
        'disabled_at': disabled_at,
        'cursor_key': cursor_key,
    }


def insert_autotopup(pgsql, autotopup):
    sql = """
        INSERT INTO bank_topup.autotopups (
            bank_uid,
            yandex_uid,
            idempotency_token,
            autotopup_id,
            autotopup_internal_id,
            type,
            enabled,
            params
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        sql,
        [
            autotopup['bank_uid'],
            autotopup['yandex_uid'],
            autotopup['idempotency_token'],
            autotopup['autotopup_id'],
            autotopup['autotopup_internal_id'],
            autotopup['type'],
            autotopup['enabled'],
            json.dumps(autotopup['params']),
        ],
    )


def update_autotopup(pgsql, autotopup):
    sql = """
        UPDATE bank_topup.autotopups
        SET
            enabled = %s,
            params = %s,
            disabled_at = %s
        WHERE autotopup_id = %s
    """
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        sql,
        [
            autotopup['enabled'],
            json.dumps(autotopup['params']),
            autotopup['disabled_at'],
            autotopup['autotopup_id'],
        ],
    )


def get_watchdog(pgsql, watchdog_id):
    cursor = pgsql['bank_topup'].cursor()
    db_fields = [
        'watchdog_id',
        'bank_uid',
        'autotopup_id',
        'autotopup_internal_id',
        'enabled_at',
        'disabled_at',
    ]
    cursor.execute(
        f'select {",".join(db_fields)} '
        f'from bank_topup.watchdogs '
        f'where watchdog_id = \'{watchdog_id}\'::UUID',
        (watchdog_id,),
    )
    rows = cursor.fetchall()
    assert len(rows) == 1
    return dict(zip(db_fields, rows[0]))


def make_watchdog(
        bank_uid=DEFAULT_YANDEX_BUID,
        execute_idempotency_token=None,
        autotopup_internal_id=DEFAULT_AUTOTOPUP_INTERNAL_ID,
        autotopup_id=DEFAULT_AUTOTOPUP_ID,
        watchdog_id=DEFAULT_WATCHDOG_ID,
        enabled_at=None,
        disabled_at=None,
):
    return {
        'bank_uid': bank_uid,
        'execute_idempotency_token': execute_idempotency_token,
        'autotopup_internal_id': autotopup_internal_id,
        'autotopup_id': autotopup_id,
        'watchdog_id': watchdog_id,
        'enabled_at': enabled_at,
        'disabled_at': disabled_at,
    }


def insert_watchdog(pgsql, watchdog):
    sql = """
        INSERT INTO bank_topup.watchdogs (
            bank_uid,
            execute_idempotency_token,
            autotopup_internal_id,
            autotopup_id,
            watchdog_id,
            disabled_at
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(
        sql,
        [
            watchdog['bank_uid'],
            watchdog['execute_idempotency_token'],
            watchdog['autotopup_internal_id'],
            watchdog['autotopup_id'],
            watchdog['watchdog_id'],
            watchdog['disabled_at'],
        ],
    )


def update_watchdog(pgsql, watchdog):
    sql = """
        UPDATE bank_topup.watchdogs
        SET disabled_at = %s
        WHERE watchdog_id = %s
    """
    cursor = pgsql['bank_topup'].cursor()
    cursor.execute(sql, [watchdog['disabled_at'], watchdog['watchdog_id']])

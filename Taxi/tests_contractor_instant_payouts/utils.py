import base64
import uuid

from Crypto.Cipher import AES


# tvmknife unittest service -s 111 -d 2345
MOCK_SERVICE_TICKET = (
    '3:serv:CBAQ__________9_IgUIbxCpEg:'
    'G4hKvC1tY887M0UUAjj13gJEnzikFS9z9so'
    'b0laeFmJ4JVL0XDyNZtWBu4ZjKf9O_juLZg'
    'hRptbnyiQRqoiBsX1eXLdABRLpdJpAxLY4d'
    'fVOD0o8GEQ7q94GH0uLQOV_POubrySzzMgN'
    'gRFhn_CwXjrfZRziFuk-RV0I-zzTsE4'
)

SERVICE_HEADERS = {'X-Ya-Service-Ticket': MOCK_SERVICE_TICKET}

# from service.yaml
CONTRACTOR_INSTANT_PAYOUTS_CRYPTO_KEY = (
    'dGVzdF9zZWNyZXRfa2V5X190ZXN0X3NlY3JldF9rZXk='
)


def build_headers(park_id, idempotency_token=None):
    headers = {
        **SERVICE_HEADERS,
        'X-Ya-User-Ticket': 'ticket_valid1',
        'X-Ya-User-Ticket-Provider': 'yandex',
        'X-Yandex-UID': '1',
        'X-Park-ID': park_id,
    }
    if idempotency_token is not None:
        headers['X-Idempotency-Token'] = idempotency_token
    return headers


def unprotect(inp):
    key = base64.b64decode(CONTRACTOR_INSTANT_PAYOUTS_CRYPTO_KEY)
    aes = AES.new(key, AES.MODE_CBC, inp[:16])
    out = aes.decrypt(inp[16:])
    return out[: -out[-1]]


def pg_dump_operation(cursor):
    cursor.execute(
        """
        SELECT
            uid,
            started_at,
            created_at,
            name,
            initiator,
            service_id,
            service_name,
            user_id,
            user_provider
        FROM
            contractor_instant_payouts.operation
    """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_account(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            contractor_instant_payouts.account
    """,
    )
    rows = {}
    for row in cursor.fetchall():
        cols = list(row)
        for idx in [12, 14]:
            if cols[idx] is not None:
                cols[idx] = str(uuid.UUID(bytes=unprotect(bytes(cols[idx]))))
        for idx in [22, 23, 24, 25, 26, 27]:
            if cols[idx] is not None:
                cols[idx] = str(unprotect(bytes(cols[idx])))[2:-1]
        rows[cols[0]] = tuple(cols[1:])
    return rows


def pg_dump_card(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            contractor_instant_payouts.card
    """,
    )
    rows = {}
    for row in cursor.fetchall():
        cols = list(row)
        for idx in [18]:
            if cols[idx] is not None:
                cols[idx] = str(uuid.UUID(bytes=unprotect(bytes(cols[idx]))))
        rows[cols[0]] = tuple(cols[1:])
    return rows


def pg_dump_card_token_session(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            contractor_instant_payouts.card_token_session
    """,
    )
    rows = {}
    for row in cursor.fetchall():
        cols = list(row)
        for idx in [15]:
            if cols[idx] is not None:
                cols[idx] = str(uuid.UUID(bytes=unprotect(bytes(cols[idx]))))
        rows[cols[0]] = tuple(cols[1:])
    return rows


def pg_dump_account_change_log(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            contractor_instant_payouts.account_change_log
    """,
    )
    return {(row[0], row[1]): row[2:] for row in cursor.fetchall()}


def pg_dump_rule(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            contractor_instant_payouts.rule
    """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_rule_change_log(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            contractor_instant_payouts.rule_change_log
    """,
    )
    return {(row[0], row[1]): row[2:] for row in cursor.fetchall()}


def pg_dump_rule_target(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            contractor_instant_payouts.rule_target
    """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_rule_target_change_log(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            contractor_instant_payouts.rule_target_change_log
    """,
    )
    return {(row[0], row[1]): row[2:] for row in cursor.fetchall()}


def pg_dump_rule_park_operation(cursor):
    cursor.execute(
        """
        SELECT
            *
        FROM
            contractor_instant_payouts.park_operation
        """,
    )
    return {row[0]: row[1:] for row in cursor.fetchall()}


def pg_dump_all(cursor):
    return {
        'operation': pg_dump_operation(cursor),
        'account': pg_dump_account(cursor),
        'card': pg_dump_card(cursor),
        'card_token_session': pg_dump_card_token_session(cursor),
        'account_change_log': pg_dump_account_change_log(cursor),
        'rule': pg_dump_rule(cursor),
        'rule_change_log': pg_dump_rule_change_log(cursor),
        'rule_target': pg_dump_rule_target(cursor),
        'rule_target_change_log': pg_dump_rule_target_change_log(cursor),
        'park_operation': pg_dump_rule_park_operation(cursor),
    }

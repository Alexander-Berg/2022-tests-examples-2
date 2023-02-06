import base64

from tests_bank_card import common

DEFAULT_TRACK_ID = 'default_track_id'


def add_operation_id(pgsql, idempotency_key):
    cursor = pgsql['bank_card'].cursor()
    cursor.execute(
        """
        INSERT INTO bank_card.operations (idempotency_key)
        VALUES (%s)
        RETURNING operation_id
    """,
        (idempotency_key,),
    )
    return cursor.fetchone()[0]


def add_authorization_info(
        pgsql,
        idempotency_key,
        params=None,
        bind_idempotency_key=common.DEFAULT_IDEMPOTENCY_TOKEN,
):
    if not params:
        params_str = (
            b'bank-card;POST v1/card/v1/set_status;'
            b'{"card_id":"some_card_id","status":"ACTIVE"};'
            b'buid_1;session_uuid_1'
        )
        params = base64.b64encode(params_str).decode()

    operation_id = add_operation_id(pgsql, idempotency_key)
    track_id = DEFAULT_TRACK_ID
    cursor = pgsql['bank_card'].cursor()
    cursor.execute(
        """
        INSERT INTO bank_card.authorization_info (
            track_id, operation_id, parameters, bind_idempotency_key)
        VALUES (%s, %s, %s, %s);
    """,
        (track_id, operation_id, params, bind_idempotency_key),
    )


def add_af_resolution(pgsql, operation_id, af_resolution):
    cursor = pgsql['bank_card'].cursor()
    cursor.execute(
        """
        INSERT INTO bank_card.antifraud_responses (
            operation_id, antifraud_resolution)
        VALUES (%s, %s)
    """,
        (operation_id, af_resolution),
    )

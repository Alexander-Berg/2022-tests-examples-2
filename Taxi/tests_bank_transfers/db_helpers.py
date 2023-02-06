import base64
from typing import List

import collections

from tests_bank_transfers import common


Transfer = collections.namedtuple(
    'Transfer',
    [
        'bank_uid',
        'agreement_id',
        'max_limit',
        'receiver_bank_id',
        'receiver_name',
        'receiver_phone',
        'currency',
        'amount',
        'comment',
        'request_id',
        'status',
        'transfer_type',
        'errors',
    ],
)

Offer = collections.namedtuple(
    'Offer',
    ['offer_id', 'transfer_id', 'currency', 'amount', 'fee', 'created_at'],
)

AuthorizationInfo = collections.namedtuple(
    'AuthorizationInfo',
    [
        'transfer_id',
        'transfer_params',
        'bank_uid',
        'antifraud_resolution',
        'antifraud_id',
        'track_id',
    ],
)


def get_transfer_params(pgsql, transfer_id, comment, amount):
    transfer = select_transfer(pgsql, transfer_id)
    if not amount:
        amount = transfer.amount
    if not comment:
        comment = transfer.comment
    params = [
        transfer_id,
        transfer.bank_uid,
        transfer.agreement_id,
        transfer.currency,
        transfer.receiver_phone,
        transfer.receiver_bank_id,
        amount,
        str(comment or ''),
    ]
    params_str = ';'.join(params)
    return (base64.b64encode(params_str.encode())).decode()


def insert_transfer(
        pgsql,
        buid=common.TEST_BANK_UID,
        agreement_id=common.TEST_AGREEMENT_ID,
        status='CREATED',
        transfer_type='C2C',
        min_limit=common.DEBIT_MIN_LIMIT,
        max_limit=common.DEBIT_MAX_LIMIT,
        receiver_phone=common.RECEIVER_PHONE_1,
        receiver_bank_id=common.TINKOFF,
        request_id=None,
        currency=common.DEFAULT_CURRENCY,
        amount=None,
        comment=None,
        errors=None,
        idempotency_token=None,
) -> str:
    receiver_name = common.get_receiver_name(receiver_phone)
    sql = """
        INSERT INTO bank_transfers.transfers (
            bank_uid,
            agreement_id,
            status,
            transfer_type,
            min_limit,
            max_limit,
            receiver_phone,
            receiver_bank_id,
            receiver_name,
            request_id,
            currency,
            amount,
            comment,
            errors,
            idempotency_token
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING
            transfer_id::TEXT
        """
    cursor = pgsql['bank_transfers'].cursor()
    cursor.execute(
        sql,
        (
            buid,
            agreement_id,
            status,
            transfer_type,
            min_limit,
            max_limit,
            receiver_phone,
            receiver_bank_id,
            receiver_name,
            request_id,
            currency,
            amount,
            comment,
            errors,
            idempotency_token,
        ),
    )
    transfer_id = cursor.fetchone()[0]
    return transfer_id


def select_transfer(pgsql, transfer_id) -> Transfer:
    sql = """
        SELECT
            bank_uid,
            agreement_id,
            max_limit,
            receiver_bank_id,
            receiver_name,
            receiver_phone,
            currency,
            amount,
            comment,
            request_id,
            status,
            transfer_type,
            errors
        FROM bank_transfers.transfers
        WHERE transfer_id = %s
        """
    cursor = pgsql['bank_transfers'].cursor()
    cursor.execute(sql, [transfer_id])
    records = cursor.fetchall()
    assert len(records) == 1
    transfer = Transfer(*(records[0]))
    return transfer


def select_transfer_history(pgsql, transfer_id) -> Transfer:
    sql = """
        SELECT
            bank_uid,
            agreement_id,
            max_limit,
            receiver_bank_id,
            receiver_name,
            receiver_phone,
            currency,
            amount,
            comment,
            request_id,
            status,
            transfer_type,
            errors
        FROM bank_transfers.transfers_history
        WHERE transfer_id = %s
        """
    cursor = pgsql['bank_transfers'].cursor()
    cursor.execute(sql, [transfer_id])
    records = cursor.fetchall()
    return [Transfer(*(records[i])) for i in range(len(records))]


def create_offer(
        pgsql,
        transfer_id,
        currency=common.DEFAULT_CURRENCY,
        amount=common.DEFAULT_OFFER_AMOUNT,
        fee=common.DEFAULT_FEE,
) -> str:
    sql = """
        INSERT INTO bank_transfers.offers (
            transfer_id,
            currency,
            amount,
            fee
        )
        VALUES (%s, %s, %s, %s)
        RETURNING
            offer_id::TEXT
    """
    cursor = pgsql['bank_transfers'].cursor()
    cursor.execute(sql, (transfer_id, currency, amount, fee))
    offer_id = cursor.fetchone()[0]
    return offer_id


def select_transfer_status(pgsql, transfer_id) -> str:
    sql = """
        SELECT status
        FROM bank_transfers.transfers
        WHERE transfer_id = %s
    """
    cursor = pgsql['bank_transfers'].cursor()
    cursor.execute(sql, [transfer_id])
    status = cursor.fetchone()[0]
    return status


def select_offer(pgsql, offer_id, transfer_id) -> Offer:
    sql = """
        SELECT
            offer_id,
            transfer_id,
            currency,
            amount,
            fee,
            created_at
    FROM bank_transfers.offers
    WHERE offer_id = %s
    AND transfer_id = %s
    """
    cursor = pgsql['bank_transfers'].cursor()
    cursor.execute(sql, [offer_id, transfer_id])
    records = cursor.fetchall()
    assert len(records) == 1
    offer = Offer(*(records[0]))
    return offer


def insert_2fa(
        pgsql,
        transfer_id,
        transfer_params=None,
        bank_uid=common.TEST_BANK_UID,
        antifraud_resolution='ALLOWED',
        track_id='default_track_id',
        antifraud_id=None,
        comment=None,
        amount=None,
):

    if transfer_params is None:
        transfer_params = get_transfer_params(
            pgsql, transfer_id, comment, amount,
        )
    sql = """
        INSERT INTO bank_transfers.authorization_info (
            transfer_id,
            transfer_params,
            bank_uid,
            antifraud_resolution,
            antifraud_id,
            track_id
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING
            transfer_id::TEXT
        """
    cursor = pgsql['bank_transfers'].cursor()
    cursor.execute(
        sql,
        (
            transfer_id,
            transfer_params,
            bank_uid,
            antifraud_resolution,
            antifraud_id,
            track_id,
        ),
    )
    transfer_id = cursor.fetchone()[0]
    return transfer_id


def select_authorization_info(pgsql, transfer_id) -> AuthorizationInfo:
    sql = """
        SELECT
            transfer_id::TEXT,
            transfer_params,
            bank_uid,
            antifraud_resolution,
            antifraud_id,
            track_id
        FROM bank_transfers.authorization_info
        WHERE transfer_id = %s
    """
    cursor = pgsql['bank_transfers'].cursor()
    cursor.execute(sql, [transfer_id])
    records = cursor.fetchall()
    assert len(records) == 1
    authorization_info = AuthorizationInfo(*(records[0]))
    return authorization_info

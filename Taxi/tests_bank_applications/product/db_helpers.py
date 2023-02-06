import collections
import json

from tests_bank_applications import common
from tests_bank_applications import db_helpers

ProductApplication = collections.namedtuple(
    'ProductApplication',
    [
        'buid',
        'status',
        'product',
        'multiple_success_status_allowed',
        'agreement_version',
        'initiator',
        'core_request_id',
        'create_idempotency_token',
        'update_idempotency_token',
        'operation_type',
        'operation_at',
        'reason',
    ],
)


def _status_to_common(status):
    if status == common.STATUS_SUBMITTED:
        return common.STATUS_PROCESSING
    if status == common.STATUS_CORE_BANKING:
        return common.STATUS_PROCESSING
    if status == common.STATUS_CANCELLED:
        return common.STATUS_FAILED
    return status


def select_application(pgsql, application_id):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT buid, status, product, multiple_success_status_allowed, '
        'agreement_version, initiator, core_request_id, '
        'create_idempotency_token, update_idempotency_token, operation_type, '
        'operation_at, reason '
        'FROM bank_applications.product '
        'WHERE application_id=%s',
        [application_id],
    )
    record = cursor.fetchone()
    if record is None:
        return None
    return ProductApplication(*record)


def select_applications_history(pgsql, application_id):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT buid, status, product, multiple_success_status_allowed, '
        'agreement_version, initiator, core_request_id, '
        'create_idempotency_token, update_idempotency_token, operation_type, '
        'operation_at, reason '
        'FROM bank_applications.product_history '
        'WHERE application_id=%s ORDER BY id',
        [application_id],
    )
    records = cursor.fetchall()
    result = []
    for record in records:
        result.append(ProductApplication(*record))
    return result


def insert_application(
        pgsql,
        buid=common.DEFAULT_YANDEX_BUID,
        status=common.STATUS_CREATED,
        multiple_success_status_allowed=False,
        product=common.PRODUCT_WALLET,
        agreement_version=0,
        core_request_id=None,
):
    initiator = json.dumps({'initiator_type': 'BUID', 'initiator_id': buid})
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        buid,
        'PRODUCT',
        _status_to_common(status),
        multiple_success_status_allowed,
    )
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'INSERT INTO bank_applications.product(application_id, buid, status, '
        'product, multiple_success_status_allowed, agreement_version, '
        'initiator, core_request_id) VALUES(%s, %s, %s, %s, %s, %s, %s, %s) '
        'RETURNING application_id',
        [
            application_id,
            buid,
            status,
            product,
            multiple_success_status_allowed,
            agreement_version,
            initiator,
            core_request_id,
        ],
    )
    return application_id


def update_status(pgsql, application_id, new_status):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'UPDATE bank_applications.product SET status = %s '
        'WHERE application_id = %s',
        [new_status, application_id],
    )
    cursor.execute(
        'UPDATE bank_applications.applications SET status = %s '
        'WHERE application_id = %s',
        [_status_to_common(new_status), application_id],
    )


def update_status_and_idempotency(
        pgsql, application_id, new_status, update_idempotency_token,
):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'UPDATE bank_applications.product SET status = %s, '
        'update_idempotency_token = %s'
        'WHERE application_id = %s',
        [new_status, update_idempotency_token, application_id],
    )
    cursor.execute(
        'UPDATE bank_applications.applications SET status = %s '
        'WHERE application_id = %s',
        [_status_to_common(new_status), application_id],
    )


def update_core_request_id(pgsql, application_id, core_request_id):
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'UPDATE bank_applications.product SET core_request_id = %s '
        'WHERE application_id = %s',
        [core_request_id, application_id],
    )

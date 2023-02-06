import json

from tests_bank_applications import common
from tests_bank_applications import db_helpers


# pylint: disable=dangerous-default-value
def insert_plus_application(
        pgsql,
        details={},
        buid=common.DEFAULT_YANDEX_BUID,
        status='PROCESSING',
):
    application_id = db_helpers.add_application(
        pgsql=pgsql,
        user_id_type='BUID',
        user_id=buid,
        application_type='PLUS',
        application_status=common.status_to_common(status),
        multiple_success_status_allowed=False,
        create_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        update_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
    )

    sql = """
    INSERT INTO bank_applications.create_plus_subscription_applications (
        application_id,
        status,
        user_id,
        user_id_type,
        details
    )
    VALUES (%s, %s, %s, 'BUID', %s)
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id, status, buid, json.dumps(details)])
    return application_id


def insert_plus_application_history(
        pgsql,
        application_id,
        status,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
):
    sql = """
    INSERT INTO bank_applications.create_plus_subscription_applications_history
    (
        application_id,
        idempotency_token,
        operation_type,
        status
    )
    VALUES (%s, %s, 'UPDATE', %s)
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id, idempotency_token, status])
    return application_id


def select_plus_application(pgsql, application_id):
    sql = """
    SELECT
        application_id,
        user_id_type,
        user_id,
        status,
        reason,
        details
    FROM bank_applications.create_plus_subscription_applications
    WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    return records[0]


def update_plus_application_status(pgsql, application_id, status):
    sql = """
    UPDATE bank_applications.create_plus_subscription_applications
    SET status = %s
    WHERE application_id = %s
    RETURNING application_id
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [status, application_id])
    records = cursor.fetchall()
    assert len(records) == 1


def select_plus_application_history(pgsql, application_id):
    sql = """
    SELECT
        application_id,
        idempotency_token,
        operation_type,
        status
    FROM bank_applications.create_plus_subscription_applications_history
    WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    return records

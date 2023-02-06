import collections
import json
from typing import Optional

from tests_bank_applications import common
from tests_bank_applications import db_helpers

Application = collections.namedtuple(
    'Application', ['user_id_type', 'user_id', 'type', 'status', 'reason'],
)


def check_asserts(pgsql, response, application_type):
    application_id = response.json()['application_id']

    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT user_id_type, user_id, type, status, '
        'initiator, additional_params '
        'FROM bank_applications.applications '
        f'WHERE application_id=\'{application_id}\';',
    )
    records = list(cursor)

    assert len(records) == 1
    assert records[0][0] == 'BUID'
    assert records[0][1] == common.DEFAULT_YANDEX_BUID
    assert records[0][4] == {
        'initiator_type': 'BUID',
        'initiator_id': common.DEFAULT_YANDEX_BUID,
    }
    assert records[0][2] == application_type
    assert records[0][3] == 'CREATED'


KycApplication = collections.namedtuple(
    'KycApplication',
    [
        'application_id',
        'status',
        'submit_idempotency_token',
        'submitted_form',
        'operation_type',
        'operation_at',
        'user_id_type',
        'user_id',
        'reason',
        'initiator',
        'procaas_init_idempotency_token',
    ],
)

KycDraftForm = collections.namedtuple(
    'KycDraftForm', ['application_id', 'form'],
)


def check_no_kyc_id_apps(pgsql):
    sql = """
        SELECT
            application_id,
            status,
            submit_idempotency_token,
            submitted_form,
            operation_type,
            operation_at
        FROM bank_applications.kyc
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql)
    records = cursor.fetchall()
    assert records == []

    history_sql = """
        SELECT
            application_id,
            status,
            submit_idempotency_token,
            submitted_form,
            operation_type,
            operation_at
        FROM bank_applications.kyc_history
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(history_sql)
    records = cursor.fetchall()
    assert records == []


def get_kyc_id_app(pgsql, application_id) -> KycApplication:
    sql = """
        SELECT
            application_id,
            status,
            submit_idempotency_token,
            submitted_form,
            operation_type,
            operation_at,
            user_id_type,
            user_id,
            reason,
            initiator,
            procaas_init_idempotency_token
        FROM bank_applications.kyc
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    result_dict = KycApplication(*(records[0]))
    return result_dict


def get_kyc_id_app_hist(pgsql, application_id) -> Optional[KycApplication]:
    sql = """
        SELECT
            application_id,
            status,
            submit_idempotency_token,
            submitted_form,
            operation_type,
            operation_at,
            user_id_type,
            user_id,
            reason,
            initiator,
            procaas_init_idempotency_token
        FROM bank_applications.kyc_history
        WHERE application_id = %s
        ORDER BY id DESC
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    return KycApplication(*(records[0])) if records else None


def insert_kyc_id_app_hist(
        pgsql,
        application_id,
        status='CREATED',
        submitted_form=None,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        operation_type='INSERT',
        buid=common.DEFAULT_YANDEX_BUID,
):
    sql = """
        INSERT INTO bank_applications.kyc_history (
            application_id,
            status,
            submitted_form,
            user_id,
            initiator,
            submit_idempotency_token,
            operation_type
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """
    initiator = json.dumps(common.INITIATOR)
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        sql,
        [
            application_id,
            status,
            submitted_form,
            buid,
            initiator,
            idempotency_token,
            operation_type,
        ],
    )


def insert_kyc_application(
        pgsql,
        submitted_form=None,
        agreement_version=0,
        submit_idempotency_token=None,
        buid=common.DEFAULT_YANDEX_BUID,
        status='PROCESSING',
        kyc_status='PROCESSING',
        create_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        update_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
):

    application_id = db_helpers.add_application(
        pgsql=pgsql,
        user_id_type='BUID',
        user_id=buid,
        application_type='KYC',
        application_status=common.status_to_common(status),
        multiple_success_status_allowed=False,
        create_idempotency_token=create_idempotency_token,
        update_idempotency_token=update_idempotency_token,
    )

    sql = """
    INSERT INTO bank_applications.kyc (
        application_id,
        status,
        submit_idempotency_token,
        user_id,
        initiator,
        submitted_form,
        agreement_version,
        operation_type
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, 'INSERT')
    """
    initiator = json.dumps(common.INITIATOR)
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        sql,
        [
            application_id,
            kyc_status,
            submit_idempotency_token,
            buid,
            initiator,
            submitted_form,
            agreement_version,
        ],
    )
    return application_id


def get_kyc_id_draft_forms(pgsql, application_id):
    sql = """
        SELECT
            application_id,
            form
        FROM bank_applications.kyc_draft_form
        WHERE application_id = %s
        ORDER BY id DESC
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    return records


def update_kyc_id_app_status(pgsql, application_id, application_status):

    sql = """
        UPDATE bank_applications.kyc
        SET status = %s
        WHERE application_id = %s
        RETURNING
        application_id
        """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, (application_status, application_id))
    application_id = cursor.fetchone()[0]
    return application_id


def add_kyc_id_application(
        pgsql,
        application_id,
        application_status,
        agreement_version='0',
        buid=common.DEFAULT_YANDEX_BUID,
):

    sql = """
        INSERT INTO bank_applications.kyc (
            application_id,
            user_id,
            initiator,
            status,
            agreement_version,
            operation_type
            )
        VALUES (%s, %s, %s, %s, %s, 'INSERT')
        RETURNING
        application_id
        """
    initiator = json.dumps(common.INITIATOR)
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        sql,
        (
            application_id,
            buid,
            initiator,
            application_status,
            agreement_version,
        ),
    )
    application_id = cursor.fetchone()[0]
    return application_id

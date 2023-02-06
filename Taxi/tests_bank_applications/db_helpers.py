# pylint: disable=too-many-lines
import collections
import json
from typing import Optional

from tests_bank_applications import common

Application = collections.namedtuple(
    'Application', ['user_id_type', 'user_id', 'type', 'status', 'reason'],
)
ApplicationRegistration = collections.namedtuple(
    'Application',
    ['yandex_uid', 'status', 'reason', 'noncritical_status', 'error'],
)


def check_asserts(
        pgsql,
        response,
        application_type,
        agreements,
        forms,
        locale='ru',
        is_uid=False,
        simplified_identification_db_check=False,
):
    if (
            application_type
            in [
                'REGISTRATION',
                'SIMPLIFIED_IDENTIFICATION',
                'DIGITAL_CARD_ISSUE',
                'SPLIT_CARD_ISSUE',
            ]
            and agreements
    ):
        if (
                locale in ('ru', 'unknown')
                and application_type != 'SIMPLIFIED_IDENTIFICATION'
        ):
            assert (
                response.json()['agreement']
                == agreements['ru'][application_type]['agreement_text']
            )
        elif locale == 'en':
            assert (
                response.json()['agreement']
                == agreements['en'][application_type]['agreement_text']
            )
        if forms:
            if application_type == 'REGISTRATION':
                assert response.json()['form'] == {
                    'phone_id': forms[application_type]['passport_phone_id'],
                    'masked_phone': forms[application_type]['masked_phone'],
                }
            elif application_type == 'SIMPLIFIED_IDENTIFICATION':
                assert response.json()['form'] == forms[application_type]
        else:
            assert 'form' not in response.json()

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
    if is_uid:
        assert records[0][0] == 'UID'
        assert records[0][1] == common.DEFAULT_YANDEX_UID
        assert records[0][4] == {
            'initiator_type': 'UID',
            'initiator_id': common.DEFAULT_YANDEX_UID,
        }
    else:
        assert records[0][0] == 'BUID'
        assert records[0][1] == common.DEFAULT_YANDEX_BUID
        assert records[0][4] == {
            'initiator_type': 'BUID',
            'initiator_id': common.DEFAULT_YANDEX_BUID,
        }
    assert records[0][2] == application_type
    assert records[0][3] == 'CREATED'
    if application_type == 'REGISTRATION':
        if forms:
            assert records[0][5] == {
                'agreement_version': 0,
                'phone_id': forms[application_type]['passport_phone_id'],
                'phone': forms[application_type]['phone'],
            }
        else:
            assert records[0][5] == {'agreement_version': 0}
            assert 'phone_id' not in records[0][5]
            assert 'phone' not in records[0][5]
    elif application_type == 'SIMPLIFIED_IDENTIFICATION':
        assert records[0][5] == {'agreement_version': 0}
        if simplified_identification_db_check:
            cursor.execute(
                'SELECT agreement_version '
                'FROM bank_applications.simplified_identification '
                f'WHERE application_id=\'{application_id}\';',
            )
            simpl_id_records = list(cursor)
            assert len(simpl_id_records) == 1
            assert simpl_id_records[0][0] == records[0][5]['agreement_version']


def check_asserts_registration(
        pgsql,
        response,
        application_type,
        agreements,
        forms,
        other_additional_params: Optional[dict] = None,
        locale='ru',
        product=common.PRODUCT_WALLET,
):
    if agreements:
        if locale in ('ru', 'unknown'):
            assert (
                response.json()['agreement']
                == agreements['ru'][application_type]['agreement_text']
            )
        elif locale == 'en':
            assert (
                response.json()['agreement']
                == agreements['en'][application_type]['agreement_text']
            )
        if forms:
            assert response.json()['form'] == {
                'phone_id': forms[application_type]['passport_phone_id'],
                'masked_phone': forms[application_type]['masked_phone'],
            }
        else:
            assert 'form' not in response.json()

    application_id = response.json()['application_id']

    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        'SELECT yandex_uid, status_text, '
        'initiator, additional_params, product_type '
        'FROM bank_applications.registration_applications '
        f'WHERE application_id=%s',
        [application_id],
    )
    records = cursor.fetchall()

    assert len(records) == 1
    assert records[0][0] == common.DEFAULT_YANDEX_UID
    assert records[0][2] == {
        'initiator_type': 'UID',
        'initiator_id': common.DEFAULT_YANDEX_UID,
    }
    assert records[0][1] == 'CREATED'
    additional_params = records[0][3]
    if forms:
        expected_params = {
            'agreement_version': 0,
            'phone_id': forms[application_type]['passport_phone_id'],
            'phone': forms[application_type]['phone'],
            'accepted_plus_offer': False,
            'has_ya_plus': False,
        }
        expected_params.update(other_additional_params or {})
        assert additional_params == expected_params
    else:
        expected_params = {
            'agreement_version': 0,
            'accepted_plus_offer': False,
            'has_ya_plus': False,
        }
        expected_params.update(other_additional_params or {})
        assert additional_params == expected_params
        assert 'phone_id' not in additional_params
        assert 'phone' not in additional_params
    assert records[0][4] == product


def add_application(
        pgsql,
        user_id_type,
        user_id,
        application_type,
        application_status,
        multiple_success_status_allowed,
        additional_params=None,
        initiator_string='buid',
        create_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        update_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
):
    initiator = json.dumps({'initiator_type': initiator_string})
    sql = """
            INSERT INTO bank_applications.applications (
              user_id_type,
              user_id,
              type,
              status,
              multiple_success_status_allowed,
              additional_params,
              initiator,
              create_idempotency_token,
              update_idempotency_token
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING
              application_id
        """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        sql,
        (
            user_id_type,
            user_id,
            application_type,
            application_status,
            multiple_success_status_allowed,
            additional_params,
            initiator,
            create_idempotency_token,
            update_idempotency_token,
        ),
    )
    application_id = cursor.fetchone()[0]
    return application_id


def reg_status_to_common(status):
    if status == 'SMS_CODE_SENT':
        return 'CREATED'
    return status


def add_application_registration(
        pgsql,
        yandex_uid,
        application_status,
        additional_params=None,
        initiator_string='buid',
        create_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        update_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
):
    application_id = add_application(
        pgsql,
        'UID',
        yandex_uid,
        'REGISTRATION',
        reg_status_to_common(application_status),
        False,
        additional_params,
        initiator_string,
        create_idempotency_token,
        update_idempotency_token,
    )
    initiator = json.dumps({'initiator_type': initiator_string})
    sql = """
            INSERT INTO bank_applications.registration_applications (
              application_id,
              yandex_uid,
              status_text,
              additional_params,
              initiator,
              create_idempotency_token,
              update_idempotency_token
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING
              application_id
        """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        sql,
        (
            application_id,
            yandex_uid,
            application_status,
            additional_params,
            initiator,
            create_idempotency_token,
            update_idempotency_token,
        ),
    )
    application_id = cursor.fetchone()[0]
    return application_id


def get_application(pgsql, application_id) -> Application:
    sql = """
        SELECT user_id_type, user_id, type, status, reason
        FROM bank_applications.applications
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    result_dict = Application(*(records[0]))
    return result_dict


def get_application_registration(
        pgsql, application_id,
) -> ApplicationRegistration:
    sql = """
        SELECT yandex_uid, status_text, reason, noncritical_status, error
        FROM bank_applications.registration_applications
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    result_dict = ApplicationRegistration(*(records[0]))
    return result_dict


def get_app_with_add_params(pgsql, application_id):
    sql = """
        SELECT additional_params, user_id_type, user_id
        FROM bank_applications.applications
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    return records[0]


def get_app_with_add_params_reg(pgsql, application_id):
    sql = """
        SELECT additional_params, yandex_uid, status_text, reason
        FROM bank_applications.registration_applications
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    return records[0]


def get_apps_by_id_in_history(pgsql, application_id):
    sql = """
        SELECT additional_params, user_id_type, user_id,
        submitted_form, update_idempotency_token, status,
        operation_type, operation_at, reason
        FROM bank_applications.applications_history
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    for record in records:
        assert record[1] == 'UID'
        assert record[2] == common.DEFAULT_YANDEX_UID
    return records


def get_apps_by_id_in_history_reg(pgsql, application_id):
    sql = """
        SELECT additional_params, yandex_uid,
        submitted_form, update_idempotency_token, status_text,
        operation_type, operation_at, reason
        FROM bank_applications.registration_applications_history
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    for record in records:
        assert record[1] == common.DEFAULT_YANDEX_UID
    return records


def update_application_status(pgsql, application_id, status):
    sql = """
        UPDATE bank_applications.applications
        SET status = %s
        WHERE application_id = %s
        RETURNING application_id
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [status, application_id])
    records = cursor.fetchall()
    assert len(records) == 1


SplitCardIssueApplication = collections.namedtuple(
    'SplitCardIssueApplication',
    [
        'application_id',
        'status',
        'agreement_id',
        'submit_idempotency_token',
        'operation_type',
        'operation_at',
    ],
)


def check_no_split_card_issue_apps(pgsql):
    sql = """
        SELECT *
        FROM bank_applications.split_card_issue_applications
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql)
    records = cursor.fetchall()
    assert records == []

    history_sql = """
        SELECT *
        FROM bank_applications.split_card_issue_applications_history
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(history_sql)
    records = cursor.fetchall()
    assert records == []


def add_split_card_issue_app(pgsql, application_id, status):
    sql = """
        INSERT INTO bank_applications.split_card_issue_applications (
            application_id, status, operation_type
        )
        VALUES (%s, %s, 'INSERT')
        RETURNING
            application_id
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id, status])
    records = cursor.fetchall()
    assert len(records) == 1


def get_split_card_issue_app(
        pgsql, application_id,
) -> SplitCardIssueApplication:
    sql = """
        SELECT
            application_id,
            status,
            agreement_id,
            submit_idempotency_token,
            operation_type,
            operation_at
        FROM bank_applications.split_card_issue_applications
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    result_dict = SplitCardIssueApplication(*(records[0]))
    return result_dict


def get_split_card_issue_app_hist(
        pgsql, application_id,
) -> SplitCardIssueApplication:
    sql = """
        SELECT
            application_id,
            status,
            agreement_id,
            submit_idempotency_token,
            operation_type,
            operation_at
        FROM bank_applications.split_card_issue_applications_history
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    result_dict = SplitCardIssueApplication(*(records[0]))
    return result_dict


def upd_split_card_issue_submit_prm(
        pgsql, application_id, status, agreement_id, submit_idempotency_token,
):
    sql = """
        UPDATE bank_applications.split_card_issue_applications
        SET
            status = %s,
            agreement_id = %s,
            submit_idempotency_token = %s
        WHERE application_id = %s
        RETURNING application_id
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        sql, [status, agreement_id, submit_idempotency_token, application_id],
    )
    records = cursor.fetchall()
    assert len(records) == 1


SimplifiedIdentificationApplication = collections.namedtuple(
    'SimplifiedIdentificationApplication',
    [
        'application_id',
        'status',
        'submit_idempotency_token',
        'submitted_form',
        'prenormalized_form',
        'operation_type',
        'operation_at',
        'user_id_type',
        'user_id',
        'reason',
        'initiator',
        'procaas_init_idempotency_token',
    ],
)

SimplifiedIdentificationDraftForm = collections.namedtuple(
    'SimplifiedIdentificationDraftForm', ['application_id', 'form'],
)


def check_no_simpl_id_apps(pgsql):
    sql = """
        SELECT
            application_id,
            status,
            submit_idempotency_token,
            submitted_form,
            operation_type,
            operation_at
        FROM bank_applications.simplified_identification
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
        FROM bank_applications.simplified_identification_history
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(history_sql)
    records = cursor.fetchall()
    assert records == []


def get_simpl_id_app(
        pgsql, application_id,
) -> SimplifiedIdentificationApplication:
    sql = """
        SELECT
            application_id,
            status,
            submit_idempotency_token,
            submitted_form,
            prenormalized_form,
            operation_type,
            operation_at,
            user_id_type,
            user_id,
            reason,
            initiator,
            procaas_init_idempotency_token
        FROM bank_applications.simplified_identification
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    result_dict = SimplifiedIdentificationApplication(*(records[0]))
    return result_dict


def get_simpl_id_app_hist(
        pgsql, application_id,
) -> Optional[SimplifiedIdentificationApplication]:
    sql = """
        SELECT
            application_id,
            status,
            submit_idempotency_token,
            submitted_form,
            prenormalized_form,
            operation_type,
            operation_at,
            user_id_type,
            user_id,
            reason,
            initiator,
            procaas_init_idempotency_token
        FROM bank_applications.simplified_identification_history
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    return (
        SimplifiedIdentificationApplication(*(records[-1]))
        if records
        else None
    )


def insert_simpl_id_app_hist(
        pgsql,
        application_id,
        status='CREATED',
        submitted_form=None,
        prenormalized_form=None,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        operation_type='INSERT',
        buid=common.DEFAULT_YANDEX_BUID,
        initiator=json.dumps(common.INITIATOR),
):
    sql = """
        INSERT INTO bank_applications.simplified_identification_history (
            application_id,
            status,
            submitted_form,
            prenormalized_form,
            user_id,
            user_id_type,
            initiator,
            submit_idempotency_token,
            operation_type
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        sql,
        [
            application_id,
            status,
            submitted_form,
            prenormalized_form,
            buid,
            common.USER_ID_TYPE_BUID,
            initiator,
            idempotency_token,
            operation_type,
        ],
    )


def insert_simpl_id_draft_form(pgsql, application_id, form):
    sql = """
        INSERT INTO bank_applications.simplified_identification_draft_form (
          application_id,
          form
        )
        VALUES (%s, %s)
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id, form])


def get_simpl_id_draft_form(
        pgsql, application_id,
) -> Optional[SimplifiedIdentificationDraftForm]:
    sql = """
        SELECT
            application_id,
            form
        FROM bank_applications.simplified_identification_draft_form
        WHERE application_id = %s
        ORDER BY id DESC
        LIMIT 1
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    return (
        SimplifiedIdentificationDraftForm(*(records[0])) if records else None
    )


def update_simpl_id_draft_form(
        pgsql, form, application_id,
) -> SimplifiedIdentificationDraftForm:
    sql = """
        UPDATE bank_applications.simplified_identification_draft_form
        SET
            form = %s
        WHERE application_id = %s
        RETURNING
            application_id,
            form
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [form, application_id])
    records = cursor.fetchall()
    result_dict = SimplifiedIdentificationDraftForm(*(records[0]))
    return result_dict


def insert_simpl_application(
        pgsql,
        submitted_form=None,
        prenormalized_form=None,
        agreement_version=0,
        submit_idempotency_token=None,
        buid=common.DEFAULT_YANDEX_BUID,
        status='PROCESSING',
        simpl_status='PROCESSING',
        create_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        update_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        initiator=json.dumps(common.INITIATOR),
):

    application_id = add_application(
        pgsql=pgsql,
        user_id_type='BUID',
        user_id=buid,
        application_type='SIMPLIFIED_IDENTIFICATION',
        application_status=common.status_to_common(status),
        multiple_success_status_allowed=False,
        create_idempotency_token=create_idempotency_token,
        update_idempotency_token=update_idempotency_token,
    )

    insert_simpl_id_draft_form(pgsql, application_id, submitted_form)

    sql = """
    INSERT INTO bank_applications.simplified_identification (
        application_id,
        status,
        submit_idempotency_token,
        user_id,
        user_id_type,
        initiator,
        submitted_form,
        prenormalized_form,
        agreement_version,
        operation_type
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'INSERT')
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        sql,
        [
            application_id,
            simpl_status,
            submit_idempotency_token,
            buid,
            common.USER_ID_TYPE_BUID,
            initiator,
            submitted_form,
            prenormalized_form,
            agreement_version,
        ],
    )
    return application_id


def get_simpl_id_draft_forms(pgsql, application_id):
    sql = """
        SELECT
            application_id,
            form
        FROM bank_applications.simplified_identification_draft_form
        WHERE application_id = %s
        ORDER BY id DESC
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    return records


def update_simpl_id_app_status(pgsql, application_id, application_status):

    sql = """
        UPDATE bank_applications.simplified_identification
        SET status = %s
        WHERE application_id = %s
        RETURNING
        application_id
        """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, (application_status, application_id))
    application_id = cursor.fetchone()[0]
    return application_id


def add_simpl_id_application(
        pgsql,
        application_id,
        application_status,
        agreement_version='0',
        buid=common.DEFAULT_YANDEX_BUID,
):

    sql = """
        INSERT INTO bank_applications.simplified_identification (
            application_id,
            user_id,
            user_id_type,
            initiator,
            status,
            agreement_version,
            operation_type
            )
        VALUES (%s, %s, %s, %s, %s, %s, 'INSERT')
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
            common.USER_ID_TYPE_BUID,
            initiator,
            application_status,
            agreement_version,
        ),
    )
    application_id = cursor.fetchone()[0]
    return application_id


SimplifiedIdentificationEsiaApplication = collections.namedtuple(
    'SimplifiedIdentificationEsiaApplication',
    [
        'application_id',
        'user_id_type',
        'user_id',
        'status',
        'initiator',
        'submit_idempotency_token',
        'procaas_init_idempotency_token',
        'redirect_url',
        'esia_state',
        'auth_code',
        'data_revision',
        'reason',
        'operation_type',
        'operation_at',
    ],
)


def select_simpl_esia_apps(pgsql, buid):
    sql = """
        SELECT
            application_id,
            user_id_type,
            user_id,
            status,
            initiator,
            submit_idempotency_token,
            procaas_init_idempotency_token,
            redirect_url,
            esia_state,
            auth_code,
            data_revision,
            reason,
            operation_type,
            operation_at
        FROM bank_applications.simplified_identification_esia
        WHERE user_id_type = \'BUID\' AND user_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [buid])
    records = cursor.fetchall()
    return list(
        map(lambda x: SimplifiedIdentificationEsiaApplication(*x), records),
    )


def select_simpl_esia_apps_hist(pgsql, application_id):
    sql = """
        SELECT
            application_id,
            user_id_type,
            user_id,
            status,
            initiator,
            submit_idempotency_token,
            procaas_init_idempotency_token,
            redirect_url,
            esia_state,
            auth_code,
            data_revision,
            reason,
            operation_type,
            operation_at
        FROM bank_applications.simplified_identification_esia_history
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    return list(
        map(lambda x: SimplifiedIdentificationEsiaApplication(*x), records),
    )


def select_simpl_esia_app(pgsql, application_id):
    sql = """
        SELECT
            application_id,
            user_id_type,
            user_id,
            status,
            initiator,
            submit_idempotency_token,
            procaas_init_idempotency_token,
            redirect_url,
            esia_state,
            auth_code,
            data_revision,
            reason,
            operation_type,
            operation_at
        FROM bank_applications.simplified_identification_esia
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    return SimplifiedIdentificationEsiaApplication(*records[0])


def insert_simpl_esia_application(
        pgsql,
        buid=common.DEFAULT_YANDEX_BUID,
        status='PROCESSING',
        simpl_esia_status='PROCESSING',
        submit_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        create_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        update_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        initiator=json.dumps(common.INITIATOR),
        redirect_url=None,
        esia_state=None,
        auth_code=None,
        data_revision=None,
):
    application_id = add_application(
        pgsql=pgsql,
        user_id_type='BUID',
        user_id=buid,
        application_type='SIMPLIFIED_IDENTIFICATION_ESIA',
        application_status=common.status_to_common(status),
        multiple_success_status_allowed=False,
        create_idempotency_token=create_idempotency_token,
        update_idempotency_token=update_idempotency_token,
    )

    sql = """
    INSERT INTO bank_applications.simplified_identification_esia (
        application_id,
        status,
        user_id,
        user_id_type,
        initiator,
        redirect_url,
        esia_state,
        auth_code,
        data_revision,
        submit_idempotency_token,
        operation_type
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'INSERT')
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(
        sql,
        [
            application_id,
            simpl_esia_status,
            buid,
            common.USER_ID_TYPE_BUID,
            initiator,
            redirect_url,
            esia_state,
            auth_code,
            data_revision,
            submit_idempotency_token,
        ],
    )
    return application_id


def update_simpl_esia_id_app_status(pgsql, application_id, application_status):
    sql = """
        UPDATE bank_applications.simplified_identification_esia
        SET status = %s
        WHERE application_id = %s
        RETURNING
        application_id
        """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, (application_status, application_id))
    application_id = cursor.fetchone()[0]
    return application_id

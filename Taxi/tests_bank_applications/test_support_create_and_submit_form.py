import collections
import json

import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


HANDLE_URL = (
    '/applications-support/v1/simplified_identification/create_and_submit_form'
)
COMMENT = 'abc'


SimplifiedIdentificationApplication = collections.namedtuple(
    'SimplifiedIdentificationApplication',
    [
        'application_id',
        'status',
        'submitted_form',
        'prenormalized_form',
        'comment',
        'initiator',
    ],
)

SimplifiedIdentificationApplicationHist = collections.namedtuple(
    'SimplifiedIdentificationApplication',
    ['status', 'submitted_form', 'prenormalized_form'],
)


def get_headers(token='allow'):
    headers = common.get_support_headers(token)
    headers['X-Idempotency-Token'] = common.DEFAULT_IDEMPOTENCY_TOKEN
    return headers


def get_applications_by_buid(pgsql, buid):
    sql = """
        SELECT
            application_id,
            status,
            submitted_form,
            prenormalized_form,
            comment,
            initiator
        FROM bank_applications.simplified_identification
        WHERE user_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [buid])
    records = cursor.fetchall()
    return [SimplifiedIdentificationApplication(*record) for record in records]


def get_applications_by_buid_hist(pgsql, buid):
    sql = """
        SELECT
            status,
            submitted_form,
            prenormalized_form
        FROM bank_applications.simplified_identification_history
        WHERE user_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [buid])
    records = cursor.fetchall()
    return [
        SimplifiedIdentificationApplicationHist(*record) for record in records
    ]


def check_null_form(
        application, status=common.STATUS_CREATED, history_table=False,
):
    assert application.status == status
    assert application.submitted_form is None
    assert application.prenormalized_form is None
    if not history_table:
        assert application.comment is None


def check_submitted(application, history_table=False):
    assert application.status == common.STATUS_SUBMITTED
    assert application.submitted_form == common.get_standard_normalized_form()
    assert (
        application.prenormalized_form == common.get_standard_submitted_form()
    )
    if not history_table:
        assert application.comment == COMMENT
        assert application.initiator['initiator_type'] == 'SUPPORT'
        assert application.initiator['initiator_id'] == common.SUPPORT_LOGIN


async def test_support_create_and_submit_simplified_identification_form(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    buid = common.DEFAULT_YANDEX_BUID
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': buid,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 200
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 2

    records = get_applications_by_buid(pgsql, buid)
    assert len(records) == 1
    check_submitted(records[0])

    application = db_helpers.get_application(pgsql, records[0].application_id)
    assert application.status == common.STATUS_PROCESSING

    records = get_applications_by_buid_hist(pgsql, buid)
    assert len(records) == 1
    check_submitted(records[0], history_table=True)


async def test_support_create_and_submit_access_control_401(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers('deny'),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


async def test_support_create_and_submit_invalid_idempotency_token(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    headers = common.get_support_headers('deny')
    headers['X-Idempotency-Token'] = '1'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=headers,
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 400


async def test_support_create_and_submit_jwt_parse_support_login_401(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers('deny'),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 401
    assert access_control_mock.apply_policies_handler.times_called == 1


@pytest.mark.parametrize('missing_field', ['buid', 'comment', 'form'])
async def test_support_create_and_submit_invalid_json(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
        missing_field,
):
    body = {
        'buid': common.DEFAULT_YANDEX_BUID,
        'comment': COMMENT,
        'form': common.get_standard_form(),
    }
    body.pop(missing_field)
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=get_headers(common.SUPPORT_TOKEN), json=body,
    )
    assert response.status_code == 400
    assert not access_control_mock.apply_policies_handler.has_calls


async def test_support_create_and_submit_invalid_form(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    form = common.get_standard_form()
    form['inn_or_snils'] = '00123123123'
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'comment': COMMENT,
            'form': form,
        },
    )
    assert response.status_code == 400
    assert access_control_mock.apply_policies_handler.has_calls


@pytest.mark.config(
    BANK_APPLICATIONS_SIMPLIFIED_IDENTIFICATION_SECOND_DOCUMENT=['SNILS'],
)
@pytest.mark.parametrize(
    'second_document,response_code', [(common.INN, 400), (common.SNILS, 200)],
)
async def test_support_create_and_submit_check_second_document(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
        second_document,
        response_code,
):
    form = common.get_standard_form()
    form['inn_or_snils'] = second_document
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'comment': COMMENT,
            'form': form,
        },
    )
    assert response.status_code == response_code
    assert access_control_mock.apply_policies_handler.has_calls


async def test_support_create_and_submit_processing_500(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
):
    taxi_processing_mock.http_status_code = 500
    taxi_processing_mock.response = {'message': '1234', 'code': '500'}
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 500
    assert access_control_mock.apply_policies_handler.has_calls
    assert taxi_processing_mock.create_event_handler.times_called == 3

    records = get_applications_by_buid(pgsql, common.DEFAULT_YANDEX_BUID)
    assert len(records) == 1
    check_submitted(records[0])

    application = db_helpers.get_application(pgsql, records[0].application_id)
    assert application.status == common.STATUS_PROCESSING

    records = get_applications_by_buid_hist(pgsql, common.DEFAULT_YANDEX_BUID)
    assert len(records) == 1
    check_submitted(records[0], history_table=True)


@pytest.mark.parametrize(
    'status', [common.STATUS_CREATED, common.STATUS_DRAFT_SAVED],
)
async def test_support_create_and_submit_old_apps_in_valid_status(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
        status,
):
    buid = common.DEFAULT_YANDEX_BUID

    if status == common.STATUS_DRAFT_SAVED:
        application_id = db_helpers.insert_simpl_application(
            pgsql,
            submitted_form=json.dumps(common.get_standard_normalized_form()),
            prenormalized_form=json.dumps(
                common.get_standard_submitted_form(),
            ),
            status=common.STATUS_CREATED,
            simpl_status=status,
        )
        db_helpers.insert_simpl_id_app_hist(
            pgsql,
            application_id,
            submitted_form=json.dumps(common.get_standard_normalized_form()),
            prenormalized_form=json.dumps(
                common.get_standard_submitted_form(),
            ),
            status=status,
        )
    else:
        application_id = db_helpers.insert_simpl_application(
            pgsql, status=status, simpl_status=status,
        )
        db_helpers.insert_simpl_id_app_hist(
            pgsql, application_id, status=status,
        )

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': buid,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 200
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 2

    records = get_applications_by_buid(pgsql, buid)
    assert len(records) == 2
    if status == common.STATUS_CREATED:
        check_null_form(records[0], status=common.STATUS_CANCELLED)
    elif status == common.STATUS_DRAFT_SAVED:
        assert records[0].status == common.STATUS_CANCELLED
        assert (
            records[0].submitted_form == common.get_standard_normalized_form()
        )
        assert (
            records[0].prenormalized_form
            == common.get_standard_submitted_form()
        )
    application = db_helpers.get_application(pgsql, records[0].application_id)
    assert application.status == common.STATUS_FAILED

    check_submitted(records[1])

    application = db_helpers.get_application(pgsql, records[1].application_id)
    assert application.status == common.STATUS_PROCESSING

    records = get_applications_by_buid_hist(pgsql, buid)
    assert len(records) == 3
    if status == common.STATUS_CREATED:
        check_null_form(records[0], status=status, history_table=True)
        check_null_form(
            records[1], status=common.STATUS_CANCELLED, history_table=True,
        )
    elif status == common.STATUS_DRAFT_SAVED:
        assert records[0].status == status
        assert (
            records[0].submitted_form == common.get_standard_normalized_form()
        )
        assert (
            records[0].prenormalized_form
            == common.get_standard_submitted_form()
        )
        assert records[1].status == common.STATUS_CANCELLED
        assert (
            records[1].submitted_form == common.get_standard_normalized_form()
        )
        assert (
            records[1].prenormalized_form
            == common.get_standard_submitted_form()
        )

    check_submitted(records[2], history_table=True)


@pytest.mark.parametrize(
    'status',
    [
        common.STATUS_PROCESSING,
        common.STATUS_AGREEMENTS_ACCEPTED,
        common.STATUS_SUBMITTED,
        common.STATUS_CORE_BANKING,
    ],
)
async def test_support_create_and_submit_old_apps_in_invalid_status(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
        status,
):
    buid = common.DEFAULT_YANDEX_BUID

    application_id = db_helpers.insert_simpl_application(
        pgsql, status=common.STATUS_PROCESSING, simpl_status=status,
    )
    db_helpers.insert_simpl_id_app_hist(pgsql, application_id, status=status)

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': buid,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 409
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.has_calls

    records = get_applications_by_buid(pgsql, buid)
    assert len(records) == 1

    records = get_applications_by_buid_hist(pgsql, buid)
    assert len(records) == 1


@pytest.mark.parametrize(
    'status',
    [
        common.STATUS_PROCESSING,
        common.STATUS_AGREEMENTS_ACCEPTED,
        common.STATUS_SUBMITTED,
        common.STATUS_CORE_BANKING,
    ],
)
async def test_support_create_and_submit_old_apps_made_by_support(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
        status,
):
    buid = common.DEFAULT_YANDEX_BUID

    application_id = db_helpers.insert_simpl_application(
        pgsql,
        status=common.STATUS_PROCESSING,
        simpl_status=status,
        submitted_form=json.dumps(common.get_standard_normalized_form()),
        initiator=json.dumps(common.SUPPORT_INITIATOR),
    )
    db_helpers.insert_simpl_id_app_hist(
        pgsql,
        application_id,
        status=status,
        initiator=json.dumps(common.SUPPORT_INITIATOR),
    )

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': buid,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 409
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.has_calls

    records = get_applications_by_buid(pgsql, buid)
    assert len(records) == 1

    records = get_applications_by_buid_hist(pgsql, buid)
    assert len(records) == 1


@pytest.mark.parametrize(
    'status',
    [
        common.STATUS_PROCESSING,
        common.STATUS_AGREEMENTS_ACCEPTED,
        common.STATUS_SUBMITTED,
        common.STATUS_CORE_BANKING,
        common.STATUS_SUCCESS,
        common.STATUS_CANCELLED,
    ],
)
async def test_support_create_and_submit_old_apps_made_by_support_conflict(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
        status,
):
    buid = common.DEFAULT_YANDEX_BUID

    old_status = common.STATUS_PROCESSING
    if status == common.STATUS_SUCCESS:
        old_status = common.STATUS_SUCCESS

    application_id = db_helpers.insert_simpl_application(
        pgsql,
        status=old_status,
        simpl_status=status,
        submitted_form=json.dumps(common.get_standard_submitted_form()),
        initiator=json.dumps(common.SUPPORT_INITIATOR),
    )
    db_helpers.insert_simpl_id_app_hist(
        pgsql,
        application_id,
        status=status,
        initiator=json.dumps(common.SUPPORT_INITIATOR),
    )

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': buid,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 409
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert not taxi_processing_mock.create_event_handler.has_calls

    records = get_applications_by_buid(pgsql, buid)
    assert len(records) == 1

    records = get_applications_by_buid_hist(pgsql, buid)
    assert len(records) == 1


@pytest.mark.parametrize('status', [common.STATUS_FAILED])
async def test_support_create_and_submit_old_apps_in_failed_status(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
        status,
):
    buid = common.DEFAULT_YANDEX_BUID

    application_id = db_helpers.insert_simpl_application(
        pgsql, status=common.STATUS_FAILED, simpl_status=status,
    )
    db_helpers.insert_simpl_id_app_hist(pgsql, application_id, status=status)

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': buid,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 200
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 2

    records = get_applications_by_buid(pgsql, buid)
    assert len(records) == 2

    check_null_form(records[0], status=status)
    application = db_helpers.get_application(pgsql, records[0].application_id)
    assert application.status == common.STATUS_FAILED

    check_submitted(records[1])
    application = db_helpers.get_application(pgsql, records[1].application_id)
    assert application.status == common.STATUS_PROCESSING

    records = get_applications_by_buid_hist(pgsql, buid)
    assert len(records) == 2
    check_null_form(records[0], status=status, history_table=True)
    check_submitted(records[1], history_table=True)


async def test_support_create_and_submit_status_changed_during_cancelling(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
        testpoint,
):
    buid = common.DEFAULT_YANDEX_BUID

    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=json.dumps(common.get_standard_normalized_form()),
        prenormalized_form=json.dumps(common.get_standard_submitted_form()),
        status=common.STATUS_CREATED,
        simpl_status=common.STATUS_CREATED,
    )
    db_helpers.insert_simpl_id_app_hist(
        pgsql,
        application_id,
        submitted_form=json.dumps(common.get_standard_normalized_form()),
        prenormalized_form=json.dumps(common.get_standard_submitted_form()),
        status=common.STATUS_CREATED,
    )

    @testpoint('cancel_conflict')
    def _insert_same_applicaton(data):
        db_helpers.update_simpl_id_app_status(
            pgsql, application_id, common.STATUS_PROCESSING,
        )

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': buid,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 500


async def test_support_create_and_submit_client_tries_cr_app_support_fail_app(
        taxi_bank_applications,
        taxi_processing_mock,
        access_control_mock,
        mockserver,
        bank_audit,
        pgsql,
        testpoint,
):
    buid = common.DEFAULT_YANDEX_BUID

    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=json.dumps(common.get_standard_normalized_form()),
        prenormalized_form=json.dumps(common.get_standard_submitted_form()),
        status=common.STATUS_CREATED,
        simpl_status=common.STATUS_CREATED,
    )
    db_helpers.insert_simpl_id_app_hist(
        pgsql,
        application_id,
        submitted_form=json.dumps(common.get_standard_normalized_form()),
        prenormalized_form=json.dumps(common.get_standard_submitted_form()),
        status=common.STATUS_CREATED,
    )

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=get_headers(common.SUPPORT_TOKEN),
        json={
            'buid': buid,
            'comment': COMMENT,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 200
    assert access_control_mock.apply_policies_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 2

    records = get_applications_by_buid(pgsql, buid)
    assert len(records) == 2

    assert records[0].status == common.STATUS_CANCELLED
    application = db_helpers.get_application(pgsql, records[0].application_id)
    assert application.status == common.STATUS_FAILED

    assert records[1].status == common.STATUS_SUBMITTED
    application = db_helpers.get_application(pgsql, records[1].application_id)
    assert application.status == common.STATUS_PROCESSING

    db_helpers.update_application_status(
        pgsql, records[1].application_id, common.STATUS_FAILED,
    )
    db_helpers.update_simpl_id_app_status(
        pgsql, records[1].application_id, common.STATUS_FAILED,
    )

    db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=json.dumps(common.get_standard_normalized_form()),
        prenormalized_form=json.dumps(common.get_standard_submitted_form()),
        status=common.STATUS_CREATED,
        simpl_status=common.STATUS_CREATED,
        create_idempotency_token='11111111-1111-1111-1111-111111111111',
    )

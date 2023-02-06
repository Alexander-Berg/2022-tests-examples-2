import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


APPLICATION_ID = 'bb2b8cc1-3bfe-45be-b952-200238d96eff'
NOT_COMMON_IDEMPOTENCY_TOKEN = 'f2af664c-24c7-4793-9cbf-19a2813454dc'
AGREEMENT_ID = 'agreement_id_123'


def default_json(application_id=APPLICATION_ID, agreement_id=AGREEMENT_ID):
    return {'application_id': application_id, 'agreement_id': agreement_id}


def add_application(pgsql, status='CREATED'):
    common_status = common.status_to_common(status)
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'SPLIT_CARD_ISSUE',
        common_status,
        multiple_success_status_allowed=False,
    )
    db_helpers.add_split_card_issue_app(pgsql, application_id, status)
    return application_id


def update_application_status(
        pgsql,
        application_id,
        status='SUBMITTED',
        agreement_id=AGREEMENT_ID,
        submit_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
):
    common_status = common.status_to_common(status)
    db_helpers.update_application_status(pgsql, application_id, common_status)
    db_helpers.upd_split_card_issue_submit_prm(
        pgsql, application_id, status, agreement_id, submit_idempotency_token,
    )


def check_stq_calls(
        stq,
        application_id,
        uid=common.DEFAULT_YANDEX_UID,
        buid=common.DEFAULT_YANDEX_BUID,
        agreement_id=AGREEMENT_ID,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
):
    assert (
        stq.bank_applications_split_card_issue_app_status_check.times_called
        == 1
    )
    stq_call = (
        stq.bank_applications_split_card_issue_app_status_check.next_call()
    )
    assert stq_call['id'] == 'bank_applications_' + idempotency_token
    stq_kwargs = stq_call['kwargs']
    stq_kwargs.pop('log_extra')
    assert stq_kwargs == {
        'buid': buid,
        'uid': uid,
        'application_id': application_id,
        'agreement_id': agreement_id,
        'idempotency_token': idempotency_token,
    }


@pytest.mark.parametrize(
    'header',
    [
        'X-Yandex-BUID',
        'X-Yandex-UID',
        'X-YaBank-SessionUUID',
        'X-YaBank-PhoneID',
    ],
)
async def test_unauthorized(taxi_bank_applications, header, pgsql):
    headers = common.headers_with_idempotency()
    headers.pop(header)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=headers,
        json=default_json(),
    )

    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


async def test_no_idempotency_token(taxi_bank_applications, pgsql):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.default_headers(),
        json=default_json(),
    )

    assert response.status_code == 400


@pytest.mark.parametrize('idempotency_token', ['', '1111', 'abc'])
async def test_invalid_idempotency_token(
        taxi_bank_applications, pgsql, idempotency_token,
):
    headers = common.default_headers()
    headers['X-Idempotency-Token'] = idempotency_token
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=headers,
        json=default_json(),
    )

    assert response.status_code == 400


@pytest.mark.parametrize('field', ['application_id', 'agreement_id'])
async def test_no_required_field(taxi_bank_applications, pgsql, field):
    req_json = default_json()
    req_json.pop(field)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=req_json,
    )

    assert response.status_code == 400


@pytest.mark.parametrize('application_id', ['', '1111', 'abc'])
async def test_invalid_appplication_id(
        taxi_bank_applications, pgsql, application_id,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(application_id),
    )

    assert response.status_code == 400


async def test_invalid_agreement_id(taxi_bank_applications, pgsql):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(agreement_id=''),
    )

    assert response.status_code == 400


async def test_appplication_id_not_found(taxi_bank_applications, pgsql):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(),
    )

    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'Can\'t find application data with requested id',
    }


@pytest.mark.parametrize('status', ['PROCESSING', 'SUCCESS', 'FAILED'])
async def test_appplication_status_not_created(
        taxi_bank_applications, pgsql, status,
):
    application_id = add_application(pgsql, status)

    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(application_id),
    )

    assert response.status_code == 409
    assert response.json() == {
        'code': 'Conflict',
        'message': 'Application is already submitted',
    }


async def test_data_race(taxi_bank_applications, stq, pgsql, testpoint):
    application_id = add_application(pgsql)

    @testpoint('data_race')
    async def _data_race(data):
        update_application_status(
            pgsql,
            application_id,
            submit_idempotency_token=NOT_COMMON_IDEMPOTENCY_TOKEN,
        )

    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(application_id),
    )

    assert response.status_code == 500

    app = db_helpers.get_split_card_issue_app(pgsql, application_id)
    assert app.status == 'SUBMITTED'
    assert app.submit_idempotency_token == NOT_COMMON_IDEMPOTENCY_TOKEN
    assert app.operation_type == 'UPDATE'

    check_stq_calls(stq, application_id)


async def test_get_application_status_data_race(
        taxi_bank_applications, stq, pgsql, testpoint,
):
    application_id = add_application(pgsql)

    @testpoint('data_race')
    async def _data_race(data):
        app = db_helpers.get_split_card_issue_app(pgsql, application_id)
        assert app.status == 'CREATED'

    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(application_id),
    )

    assert response.status_code == 200

    check_stq_calls(stq, application_id)


async def test_ok(taxi_bank_applications, stq, pgsql):
    application_id = add_application(pgsql)

    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(application_id),
    )

    assert response.status_code == 200

    common_app = db_helpers.get_application(pgsql, application_id)
    assert common_app.status == 'PROCESSING'

    app = db_helpers.get_split_card_issue_app(pgsql, application_id)
    assert app.status == 'SUBMITTED'
    assert app.submit_idempotency_token == common.DEFAULT_IDEMPOTENCY_TOKEN
    assert app.operation_type == 'UPDATE'

    history_app = db_helpers.get_split_card_issue_app_hist(
        pgsql, application_id,
    )
    assert history_app == app

    check_stq_calls(stq, application_id)


async def test_ok_with_retry(taxi_bank_applications, stq, pgsql):
    application_id = add_application(pgsql)

    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(application_id),
    )

    assert response.status_code == 200
    app = db_helpers.get_split_card_issue_app(pgsql, application_id)
    assert app.status == 'SUBMITTED'

    response2 = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(application_id),
    )

    assert response2.status_code == 200
    app = db_helpers.get_split_card_issue_app(pgsql, application_id)
    assert app.status == 'SUBMITTED'


async def test_ok_with_retry_another_token(taxi_bank_applications, stq, pgsql):
    application_id = add_application(pgsql)

    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(application_id),
    )

    assert response.status_code == 200
    app = db_helpers.get_split_card_issue_app(pgsql, application_id)
    assert app.status == 'SUBMITTED'

    headers = common.default_headers()
    headers['X-Idempotency-Token'] = NOT_COMMON_IDEMPOTENCY_TOKEN
    response2 = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=headers,
        json=default_json(application_id),
    )

    assert response2.status_code == 409
    assert response2.json() == {
        'code': 'Conflict',
        'message': 'Application is already submitted',
    }

    check_stq_calls(stq, application_id)


async def test_ok_with_retry_another_agreement_id(
        taxi_bank_applications, stq, pgsql,
):
    application_id = add_application(pgsql)

    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(application_id),
    )

    assert response.status_code == 200
    app = db_helpers.get_split_card_issue_app(pgsql, application_id)
    assert app.status == 'SUBMITTED'
    assert app.agreement_id == AGREEMENT_ID
    assert app.submit_idempotency_token == common.DEFAULT_IDEMPOTENCY_TOKEN

    response2 = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/submit',
        headers=common.headers_with_idempotency(),
        json=default_json(application_id, 'INVALID_AGREEMENT'),
    )

    assert response2.status_code == 409
    assert response2.json() == {
        'code': 'Conflict',
        'message': 'Application has another agreement_id',
    }

    check_stq_calls(stq, application_id)


# STQ tests


def default_stq_kwargs(
        application_id,
        buid=common.DEFAULT_YANDEX_BUID,
        uid=common.DEFAULT_YANDEX_UID,
        agreement_id=AGREEMENT_ID,
        idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
):
    return {
        'buid': buid,
        'uid': uid,
        'application_id': application_id,
        'agreement_id': agreement_id,
        'idempotency_token': idempotency_token,
    }


async def test_stq_task_created_application(
        mockserver,
        taxi_bank_applications,
        stq_runner,
        taxi_processing_mock,
        pgsql,
        stq_agent,
):
    application_id = add_application(pgsql)

    await stq_runner.bank_applications_split_card_issue_app_status_check.call(
        task_id='id',
        kwargs=default_stq_kwargs(application_id),
        expect_fail=False,
    )

    assert taxi_processing_mock.create_event_handler.times_called == 0
    assert stq_agent.reschedule.times_called == 1


async def test_stq_task_submitted_application(
        mockserver,
        taxi_bank_applications,
        stq_runner,
        taxi_processing_mock,
        pgsql,
        stq_agent,
):
    application_id = add_application(pgsql, 'SUBMITTED')

    await stq_runner.bank_applications_split_card_issue_app_status_check.call(
        task_id='id',
        kwargs=default_stq_kwargs(application_id),
        expect_fail=False,
    )

    assert taxi_processing_mock.create_event_handler.times_called == 1
    assert stq_agent.reschedule.times_called == 0


@pytest.mark.parametrize('status', ['PROCESSING', 'SUCCESS', 'FAILED'])
async def test_stq_task_already_processed_application(
        mockserver,
        taxi_bank_applications,
        stq_runner,
        taxi_processing_mock,
        pgsql,
        stq_agent,
        status,
):
    application_id = add_application(pgsql, status)

    await stq_runner.bank_applications_split_card_issue_app_status_check.call(
        task_id='id',
        kwargs=default_stq_kwargs(application_id),
        expect_fail=False,
    )

    assert taxi_processing_mock.create_event_handler.times_called == 0
    assert stq_agent.reschedule.times_called == 0


async def test_stq_task_ok(
        mockserver,
        taxi_bank_applications,
        stq_runner,
        taxi_processing_mock,
        pgsql,
        stq_agent,
):
    application_id = add_application(pgsql)

    await stq_runner.bank_applications_split_card_issue_app_status_check.call(
        task_id='id',
        kwargs=default_stq_kwargs(application_id),
        expect_fail=False,
    )

    assert taxi_processing_mock.create_event_handler.times_called == 0
    assert stq_agent.reschedule.times_called == 1

    update_application_status(pgsql, application_id)

    await stq_runner.bank_applications_split_card_issue_app_status_check.call(
        task_id='id',
        kwargs=default_stq_kwargs(application_id),
        expect_fail=False,
    )

    assert taxi_processing_mock.create_event_handler.times_called == 1
    assert stq_agent.reschedule.times_called == 1


async def test_stq_procaas_fails(
        mockserver,
        taxi_bank_applications,
        stq_runner,
        taxi_processing_mock,
        pgsql,
        stq_agent,
):
    application_id = add_application(pgsql, 'SUBMITTED')

    taxi_processing_mock.set_http_status_code(500)

    await stq_runner.bank_applications_split_card_issue_app_status_check.call(
        task_id='id',
        kwargs=default_stq_kwargs(application_id),
        expect_fail=True,
    )

    assert taxi_processing_mock.create_event_handler.times_called == 3
    assert stq_agent.reschedule.times_called == 0

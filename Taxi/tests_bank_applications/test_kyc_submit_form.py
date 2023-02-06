import json

import pytest

from tests_bank_applications import common
from tests_bank_applications import kyc_db_helpers

LAST_NAME = 'иванов'
MIDDLE_NAME = 'иванович'
FIRST_NAME = 'иван'
PASSPORT_NUMBER = '1212654321'
BIRTHDAY = '2000-01-01'
SNILS = '08976857866'
INN = '123456789012'


def change_uuid(uuid):
    return uuid[:-1] + ('1' if uuid[-1] != '1' else '2')


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
async def test_kyc_submit_application(
        taxi_bank_applications,
        mockserver,
        taxi_processing_mock,
        pgsql,
        bank_audit,
):
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=headers,
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']
    kyc_application = kyc_db_helpers.get_kyc_id_app(pgsql, application_id)
    submitted_form = kyc_application.submitted_form
    assert submitted_form is None

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/submit_form',
        headers=common.headers_with_idempotency(),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': application_id,
            'form': common.get_kyc_standard_form(),
        },
    )

    assert response.status_code == 200

    kyc_application = kyc_db_helpers.get_kyc_id_app(pgsql, application_id)
    assert kyc_application.submitted_form == common.get_kyc_standard_form()

    history_kyc_application = kyc_db_helpers.get_kyc_id_app_hist(
        pgsql, application_id,
    )
    assert (
        history_kyc_application.submitted_form
        == common.get_kyc_standard_form()
    )
    assert taxi_processing_mock.create_event_handler.times_called == 2


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
async def test_kyc_submit_application_not_found(
        taxi_bank_applications, mockserver, taxi_processing_mock, bank_audit,
):
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=headers,
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/submit_form',
        headers=common.headers_with_idempotency(),
        json={
            'application_id': change_uuid(application_id),
            'buid': common.DEFAULT_YANDEX_BUID,
            'form': common.get_kyc_standard_form(),
        },
    )

    assert response.status_code == 404


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
async def test_kyc_submit_already_handled(
        taxi_bank_applications,
        mockserver,
        taxi_processing_mock,
        pgsql,
        bank_audit,
):
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=headers,
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/submit_form',
        headers=common.headers_with_idempotency(),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': application_id,
            'form': common.get_kyc_standard_form(),
        },
    )

    assert response.status_code == 200

    kyc_application = kyc_db_helpers.get_kyc_id_app(pgsql, application_id)
    submitted_form = kyc_application.submitted_form
    assert submitted_form == common.get_kyc_standard_form()

    history_kyc_application = kyc_db_helpers.get_kyc_id_app_hist(
        pgsql, application_id,
    )
    history_submitted_form = history_kyc_application.submitted_form
    assert history_submitted_form == common.get_kyc_standard_form()
    assert taxi_processing_mock.create_event_handler.times_called == 2

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/submit_form',
        headers=common.headers_with_idempotency(),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': application_id,
            'form': common.get_kyc_standard_form(),
        },
    )

    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 2


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
async def test_kyc_submit_state_conflict(
        taxi_bank_applications,
        mockserver,
        taxi_processing_mock,
        pgsql,
        bank_audit,
):
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=headers,
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/submit_form',
        headers=common.headers_with_idempotency(),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': application_id,
            'form': common.get_kyc_standard_form(),
        },
    )

    assert response.status_code == 200

    kyc_application = kyc_db_helpers.get_kyc_id_app(pgsql, application_id)
    submitted_form = kyc_application.submitted_form
    assert submitted_form == common.get_kyc_standard_form()

    history_kyc_application = kyc_db_helpers.get_kyc_id_app_hist(
        pgsql, application_id,
    )
    history_submitted_form = history_kyc_application.submitted_form
    assert history_submitted_form == common.get_kyc_standard_form()

    assert taxi_processing_mock.create_event_handler.times_called == 2

    new_headers = common.headers_with_idempotency()
    new_headers['X-Idempotency-Token'] = change_uuid(
        common.DEFAULT_IDEMPOTENCY_TOKEN,
    )
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/submit_form',
        headers=new_headers,
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': application_id,
            'form': common.get_kyc_standard_form(),
        },
    )

    assert response.status_code == 409


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
@pytest.mark.parametrize(
    'status,procaas_count', [('PROCESSING', 0), ('SUCCESS', 0), ('FAILED', 0)],
)
async def test_kyc_submit_ok_submitted(
        taxi_bank_applications,
        mockserver,
        taxi_processing_mock,
        pgsql,
        bank_audit,
        status,
        procaas_count,
):
    application_id = kyc_db_helpers.insert_kyc_application(
        pgsql,
        kyc_status=status,
        submit_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        submitted_form=json.dumps(common.get_kyc_standard_form()),
    )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/submit_form',
        headers=common.headers_with_idempotency(),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': application_id,
            'form': common.get_kyc_standard_form(),
        },
    )
    assert response.status_code == 200
    assert (
        taxi_processing_mock.create_event_handler.times_called == procaas_count
    )


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
@pytest.mark.parametrize(
    'idempotency_token,form',
    [
        (common.DEFAULT_IDEMPOTENCY_TOKEN, common.get_kyc_standard_form()),
        (common.NOT_DEFAULT_IDEMPOTENCY_TOKEN, common.get_kyc_standard_form()),
    ],
)
async def test_kyc_submit_ok_conflict(
        taxi_bank_applications,
        mockserver,
        taxi_processing_mock,
        pgsql,
        bank_audit,
        idempotency_token,
        form,
):
    if idempotency_token == common.DEFAULT_IDEMPOTENCY_TOKEN:
        form['first_name'] = 'other_name'

    application_id = kyc_db_helpers.insert_kyc_application(
        pgsql,
        submit_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        submitted_form=json.dumps(common.get_kyc_standard_form()),
    )

    headers = common.default_headers()
    headers['X-Idempotency-Token'] = idempotency_token
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/submit_form',
        headers=headers,
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': application_id,
            'form': form,
        },
    )
    assert response.status_code == 409
    assert taxi_processing_mock.create_event_handler.times_called == 0


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
async def test_kyc_submit_ok_procaas_failed(
        taxi_bank_applications,
        mockserver,
        taxi_processing_mock,
        pgsql,
        bank_audit,
):
    application_id = kyc_db_helpers.insert_kyc_application(
        pgsql, status='CREATED', kyc_status='CREATED',
    )

    taxi_processing_mock.set_http_status_code(500)

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/submit_form',
        headers=common.headers_with_idempotency(),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': application_id,
            'form': common.get_kyc_standard_form(),
        },
    )
    assert response.status_code == 500
    assert taxi_processing_mock.create_event_handler.times_called == 3

    kyc_application = kyc_db_helpers.get_kyc_id_app(pgsql, application_id)
    assert kyc_application.status == 'PROCESSING'
    assert kyc_application.submitted_form == common.get_kyc_standard_form()
    assert (
        kyc_application.submit_idempotency_token
        == common.DEFAULT_IDEMPOTENCY_TOKEN
    )

    taxi_processing_mock.set_http_status_code(200)

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/submit_form',
        headers=common.headers_with_idempotency(),
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': application_id,
            'form': common.get_kyc_standard_form(),
        },
    )
    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 3

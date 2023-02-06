import json

import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers
from tests_bank_applications import kyc_db_helpers


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
@pytest.mark.parametrize(
    'buid', ['nok', 'invalid'],  # disabled in exp  # not in exp
)
async def test_kyc_user_is_not_in_exp(
        taxi_bank_applications, mockserver, bank_audit, buid, pgsql,
):
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/create_application',
        json={'buid': buid},
        headers=headers,
    )
    assert response.status_code == 404
    kyc_db_helpers.check_no_kyc_id_apps(pgsql)


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
async def test_kyc_no_last_application_ok(
        taxi_bank_applications, taxi_processing_mock, pgsql, bank_audit,
):
    headers = common.default_headers()
    response = await taxi_bank_applications.post(
        '/applications-internal/v1/kyc/create_application',
        headers=headers,
        json={'buid': common.DEFAULT_YANDEX_BUID},
    )
    assert response.status_code == 200

    resp_json = response.json()
    application_id = resp_json.get('application_id')

    assert len(resp_json) == 2
    assert application_id
    assert len(application_id) > 1
    assert resp_json['status'] == 'CREATED'

    kyc_db_helpers.check_asserts(pgsql, response, 'KYC')

    app = kyc_db_helpers.get_kyc_id_app(pgsql, application_id)
    assert app.status == 'CREATED'
    assert not getattr(app, 'submit_idempotency_token')
    assert app.operation_type == 'INSERT'
    assert app.submitted_form is None
    assert app.initiator == common.INITIATOR
    assert app.user_id_type == common.USER_ID_TYPE_BUID
    assert app.user_id == common.DEFAULT_YANDEX_BUID
    assert app.reason is None
    assert app.procaas_init_idempotency_token

    history_app = kyc_db_helpers.get_kyc_id_app_hist(pgsql, application_id)
    assert history_app == app

    assert taxi_processing_mock.create_event_handler.times_called == 1


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
async def test_kyc_procaas_error(
        taxi_bank_applications,
        bank_audit,
        bank_core_client_mock,
        taxi_processing_mock,
        pgsql,
):
    taxi_processing_mock.set_http_status_code(500)
    response = await taxi_bank_applications.post(
        '/applications-internal/v1/kyc/create_application',
        headers=common.default_headers(),
        json={'buid': common.DEFAULT_YANDEX_BUID},
    )
    assert response.status_code == 500


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
@pytest.mark.parametrize('status', ['CREATED', 'PROCESSING', 'SUCCESS'])
async def test_kyc_create_application_with_last_application(
        taxi_bank_applications,
        taxi_processing_mock,
        pgsql,
        status,
        bank_audit,
):
    headers = common.default_headers()
    last_app_response = await taxi_bank_applications.post(
        '/applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=headers,
    )
    assert last_app_response.status_code == 200

    resp_json = last_app_response.json()
    application_id = resp_json.get('application_id')
    kyc_db_helpers.update_kyc_id_app_status(pgsql, application_id, status)

    response = await taxi_bank_applications.post(
        '/applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=headers,
    )

    if status == 'SUCCESS':
        assert response.status_code == 409
    else:
        assert response.status_code == 200
        app = kyc_db_helpers.get_kyc_id_app(pgsql, application_id)
        assert app.status == 'CREATED' if status == 'CREATED' else 'PROCESSING'
        assert not getattr(app, 'submit_idempotency_token')
        assert taxi_processing_mock.create_event_handler.has_calls
        assert (
            taxi_processing_mock.create_event_handler.times_called == 2
            if status == 'CREATED'
            else 1
        )


@pytest.mark.parametrize(
    'application_status', ['CREATED', 'PROCESSING', 'FAILED', 'SUCCESS'],
)
@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
async def test_kyc_application_not_in_kyc_db(
        taxi_bank_applications,
        taxi_processing_mock,
        pgsql,
        application_status,
        bank_audit,
):
    headers = common.default_headers()
    db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'KYC',
        application_status,
        False,
    )

    response = await taxi_bank_applications.post(
        '/applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=headers,
    )
    assert response.status_code == 500


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
async def test_kyc_race_condition(
        taxi_bank_applications,
        taxi_processing_mock,
        pgsql,
        testpoint,
        bank_audit,
):
    headers = common.default_headers()

    @testpoint('data_race')
    async def _data_race(data):
        kyc_db_helpers.insert_kyc_application(
            pgsql,
            submitted_form=json.dumps(common.get_standard_submitted_form()),
            agreement_version=2,
            status=common.STATUS_CREATED,
        )

    response = await taxi_bank_applications.post(
        '/applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=headers,
    )
    assert response.status_code == 500


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
async def test_kyc_last_failed_application(
        taxi_bank_applications, taxi_processing_mock, pgsql, bank_audit,
):
    kyc_db_helpers.insert_kyc_application(
        pgsql,
        submitted_form=json.dumps(common.get_standard_submitted_form()),
        agreement_version=2,
        status=common.STATUS_FAILED,
        kyc_status=common.STATUS_FAILED,
        create_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
        update_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
        submit_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
    )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=common.default_headers(),
    )
    assert response.status_code == 200


@pytest.mark.experiments3(filename='bank_kyc_feature_experiments.json')
@pytest.mark.parametrize('status', ['CREATED', 'DRAFT_SAVED'])
async def test_kyc_two_applications_with_failed(
        taxi_bank_applications,
        taxi_processing_mock,
        pgsql,
        bank_audit,
        status,
):
    kyc_db_helpers.insert_kyc_application(
        pgsql,
        submitted_form=json.dumps(common.get_standard_submitted_form()),
        status=common.STATUS_FAILED,
        create_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
        update_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
        submit_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
    )

    kyc_db_helpers.insert_kyc_application(
        pgsql,
        submitted_form=json.dumps(common.get_standard_submitted_form()),
        status='CREATED',
        kyc_status=status,
    )

    response = await taxi_bank_applications.post(
        'applications-internal/v1/kyc/create_application',
        json={'buid': common.DEFAULT_YANDEX_BUID},
        headers=common.default_headers(),
    )

    assert response.status_code == 200

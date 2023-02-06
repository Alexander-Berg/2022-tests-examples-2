import json

import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

PUBLIC_HANDLE = '/v1/applications/v1/simplified_identification/submit_form'
INTERNAL_HANDLE = (
    '/applications-internal/v1/simplified_identification/submit_form'
)


def assert_defaults(pgsql, application_id):
    application = db_helpers.get_simpl_id_app(
        pgsql=pgsql, application_id=application_id,
    )

    assert (
        application.submit_idempotency_token
        == common.DEFAULT_IDEMPOTENCY_TOKEN
    )
    assert (
        application.prenormalized_form == common.get_standard_submitted_form()
    )
    assert application.submitted_form == common.get_standard_normalized_form()

    record = db_helpers.get_simpl_id_app_hist(
        pgsql=pgsql, application_id=application_id,
    )
    assert record.application_id == application_id
    assert record.prenormalized_form == common.get_standard_submitted_form()
    assert record.submitted_form == common.get_standard_normalized_form()

    record = db_helpers.get_simpl_id_draft_form(
        pgsql=pgsql, application_id=application_id,
    )
    assert record.application_id == application_id
    assert record.form == common.get_standard_normalized_form()


def change_uuid(uuid):
    return uuid[:-1] + ('1' if uuid[-1] != '1' else '2')


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_simplified_identification_submit_application(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        stq,
        pgsql,
):
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/create_application',
        headers=common.default_headers(locale='ru'),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']
    application = db_helpers.get_simpl_id_app(
        pgsql=pgsql, application_id=application_id,
    )
    assert application.status == 'CREATED'
    assert application.submitted_form is None
    assert application.prenormalized_form is None

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )

    assert response.status_code == 200

    assert_defaults(pgsql, application_id)

    assert taxi_processing_mock.create_event_handler.times_called == 2


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_simplified_identification_submit_application_internal(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        stq,
        pgsql,
):
    response = await taxi_bank_applications.post(
        '/applications-internal/v1/'
        'simplified_identification/create_application',
        json={
            'yandex_uid': common.DEFAULT_YANDEX_UID,
            'yandex_buid': common.DEFAULT_YANDEX_BUID,
            'locale': common.DEFAULT_LANGUAGE,
            'remote_ip': common.SOME_IP,
        },
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']
    application = db_helpers.get_simpl_id_app(
        pgsql=pgsql, application_id=application_id,
    )
    assert application.status == 'CREATED'
    assert application.submitted_form is None
    assert application.prenormalized_form is None

    response = await taxi_bank_applications.post(
        INTERNAL_HANDLE,
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'application_id': application_id,
            'yandex_buid': common.DEFAULT_YANDEX_BUID,
            'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
            'remote_ip': common.SOME_IP,
            'form': common.get_standard_form(),
        },
    )

    assert response.status_code == 200

    assert_defaults(pgsql, application_id)

    assert taxi_processing_mock.create_event_handler.times_called == 2


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.config(
    BANK_APPLICATIONS_SIMPLIFIED_IDENTIFICATION_SECOND_DOCUMENT=['SNILS'],
)
@pytest.mark.parametrize(
    'second_document,response_code', [(common.INN, 400), (common.SNILS, 200)],
)
async def test_simplified_identification_check_valid_second_document(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        stq,
        pgsql,
        bank_audit,
        second_document,
        response_code,
):
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/create_application',
        headers=common.default_headers(locale='ru'),
    )

    assert response.status_code == 200
    assert response.json()['second_documents'] == ['SNILS']

    application_id = response.json()['application_id']
    application = db_helpers.get_simpl_id_app(
        pgsql=pgsql, application_id=application_id,
    )
    assert application.prenormalized_form is None
    assert application.submitted_form is None

    form = common.get_standard_form()
    form['inn_or_snils'] = second_document
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={'application_id': application_id, 'form': form},
    )

    assert response.status_code == response_code


@pytest.mark.parametrize('missed_header', ['X-Yandex-UID', 'X-Yandex-BUID'])
@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_simplified_identification_submit_not_authorized(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        missed_header,
):
    headers = common.default_headers(locale='ru')
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/create_application',
        headers=headers,
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    headers = common.headers_with_idempotency()
    headers.pop(missed_header)
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=headers,
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )

    assert response.status_code == 401


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_simplified_identification_submit_application_not_found(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
):
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/create_application',
        headers=common.default_headers(locale='ru'),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={
            'application_id': change_uuid(application_id),
            'form': common.get_standard_form(),
        },
    )

    assert response.status_code == 404


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_simplified_identification_submit_already_handled(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        stq,
        pgsql,
):
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/create_application',
        headers=common.default_headers(locale='ru'),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )

    assert response.status_code == 200

    assert_defaults(pgsql, application_id)

    assert taxi_processing_mock.create_event_handler.times_called == 2

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )

    assert response.status_code == 200

    assert_defaults(pgsql, application_id)

    assert taxi_processing_mock.create_event_handler.times_called == 3


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_simplified_identification_submit_state_conflict(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        stq,
        pgsql,
):
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/create_application',
        headers=common.default_headers(locale='ru'),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )

    assert response.status_code == 200

    assert_defaults(pgsql, application_id)

    assert taxi_processing_mock.create_event_handler.times_called == 2

    new_headers = common.headers_with_idempotency(
        change_uuid(common.DEFAULT_IDEMPOTENCY_TOKEN),
    )
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=new_headers,
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )

    assert response.status_code == 409


@pytest.mark.parametrize(
    'field,invalid_value',
    [
        ('first_name', ''),
        ('last_name', ''),
        ('passport_number', '1'),
        ('inn_or_snils', '1'),
        ('first_name', 'Анна  '),
    ],
)
@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_simplified_identification_submit_invalid_form_data(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        pgsql,
        field,
        invalid_value,
):
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/create_application',
        headers=common.default_headers(locale='ru'),
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    form = common.get_standard_form()
    form[field] = invalid_value
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={'application_id': application_id, 'form': form},
    )

    assert response.status_code == 400


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_get_application_data(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        bank_forms_mock,
        stq,
        pgsql,
        testpoint,
        blackbox_mock,
):
    application_type = 'SIMPLIFIED_IDENTIFICATION'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/create_application',
        headers=common.default_headers(),
        json={'type': application_type},
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    @testpoint('get_application_data_race')
    async def _get_application_data_race(data):
        response = await taxi_bank_applications.post(
            '/applications-internal/v1/'
            'simplified_identification/get_application_data',
            headers=common.default_headers(),
            json={'application_id': application_id},
        )
        assert response.status_code == 200
        assert response.json()['form'] == common.get_standard_normalized_form()
        assert response.json()['agreement_version'] == 0

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize(
    'error_type, request_app_id, response_code',
    [
        ('none', 'later', 200),
        ('app_id_format', 'ivalid', 400),
        ('404', '89389e2d-3291-4bc0-baa0-27aa91908650', 404),
    ],
)
async def test_get_application_data_sql(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        pgsql,
        testpoint,
        blackbox_mock,
        error_type,
        request_app_id,
        response_code,
):
    result_form = common.get_standard_submitted_form()
    form = json.dumps(result_form)
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=form,
        prenormalized_form=form,
        agreement_version=2,
    )

    if error_type == 'none':
        request_app_id = application_id

    response = await taxi_bank_applications.post(
        '/applications-internal/v1/'
        'simplified_identification/get_application_data',
        headers=common.default_headers(),
        json={'application_id': request_app_id},
    )
    assert response.status_code == response_code
    if error_type == 'none':
        assert response.json()['form'] == result_form
        assert response.json()['agreement_version'] == 2


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize(
    'result_form',
    [
        {
            'last_name': common.LAST_NAME,
            'first_name': common.FIRST_NAME,
            'middle_name': common.MIDDLE_NAME,
            'passport_number': common.PASSPORT_NUMBER,
            'birthday': common.BIRTHDAY,
            'inn': common.INN,
        },
        {
            'last_name': common.LAST_NAME,
            'first_name': common.FIRST_NAME,
            'passport_number': common.PASSPORT_NUMBER,
            'birthday': common.BIRTHDAY,
            'snils': common.SNILS,
        },
        common.get_standard_submitted_form(),
    ],
)
async def test_get_application_data_form(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        bank_forms_mock,
        pgsql,
        testpoint,
        blackbox_mock,
        result_form,
):
    form = json.dumps(result_form)
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=form,
        prenormalized_form=form,
        agreement_version=2,
    )

    response = await taxi_bank_applications.post(
        '/applications-internal/v1/'
        'simplified_identification/get_application_data',
        headers=common.default_headers(),
        json={'application_id': application_id},
    )
    assert response.status_code == 200
    assert response.json()['form'] == result_form
    assert response.json()['agreement_version'] == 2


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize('status', ['CREATED', 'DRAFT_SAVED'])
async def test_simplified_identification_submit_ok_created(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        stq,
        pgsql,
        status,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql, status='CREATED', simpl_status=status,
    )

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 1

    db_res = db_helpers.get_simpl_id_app(pgsql, application_id)
    assert db_res.status == 'SUBMITTED'
    assert db_res.submitted_form == common.get_standard_normalized_form()
    assert db_res.submit_idempotency_token == common.DEFAULT_IDEMPOTENCY_TOKEN


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize(
    'status,procaas_count',
    [('SUBMITTED', 1), ('PROCESSING', 0), ('SUCCESS', 0), ('FAILED', 0)],
)
async def test_simplified_identification_submit_ok_submitted(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        stq,
        pgsql,
        status,
        procaas_count,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        simpl_status=status,
        submit_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        submitted_form=json.dumps(common.get_standard_normalized_form()),
        prenormalized_form=json.dumps(common.get_standard_submitted_form()),
    )

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 200
    assert (
        taxi_processing_mock.create_event_handler.times_called == procaas_count
    )


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize(
    'idempotency_token,form',
    [
        (
            common.DEFAULT_IDEMPOTENCY_TOKEN,
            {
                'last_name': 'Нестандартное',
                'first_name': 'Имя',
                'middle_name': common.MIDDLE_NAME,
                'passport_number': common.PASSPORT_NUMBER,
                'birthday': common.BIRTHDAY,
                'inn_or_snils': common.SNILS,
            },
        ),
        (common.NOT_DEFAULT_IDEMPOTENCY_TOKEN, common.get_standard_form()),
    ],
)
async def test_simplified_identification_submit_ok_conflict(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        stq,
        pgsql,
        idempotency_token,
        form,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submit_idempotency_token=common.DEFAULT_IDEMPOTENCY_TOKEN,
        submitted_form=json.dumps(common.get_standard_normalized_form()),
        prenormalized_form=json.dumps(common.get_standard_submitted_form()),
    )

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(idempotency_token),
        json={'application_id': application_id, 'form': form},
    )
    assert response.status_code == 409
    assert taxi_processing_mock.create_event_handler.times_called == 0


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_simplified_identification_submit_ok_procaas_failed(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        stq,
        pgsql,
):
    application_id = db_helpers.insert_simpl_application(
        pgsql, status='CREATED', simpl_status='CREATED',
    )

    taxi_processing_mock.set_http_status_code(500)

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 500
    assert taxi_processing_mock.create_event_handler.times_called == 3

    db_res = db_helpers.get_simpl_id_app(pgsql, application_id)
    assert db_res.status == 'SUBMITTED'
    assert db_res.submitted_form == common.get_standard_normalized_form()
    assert db_res.submit_idempotency_token == common.DEFAULT_IDEMPOTENCY_TOKEN

    taxi_processing_mock.set_http_status_code(200)

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(),
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )
    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 4


async def test_submit_app_in_status_submitted_with_deleted_submitted_form(
        taxi_bank_applications, mockserver, taxi_processing_mock,
):
    application_id = '11111111-1111-1111-1111-111111111111'
    idempotency_token = '11111111-1111-1111-1111-111111111112'

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.headers_with_idempotency(idempotency_token),
        json={
            'application_id': application_id,
            'form': common.get_standard_form(),
        },
    )

    assert response.status_code == 200
    assert not taxi_processing_mock.create_event_handler.has_calls

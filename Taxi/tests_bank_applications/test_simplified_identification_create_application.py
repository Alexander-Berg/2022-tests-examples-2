import json

import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

PUBLIC_HANDLE = (
    '/v1/applications/v1/simplified_identification/create_application'
)
INTERNAL_HANDLE = (
    '/applications-internal/v1/simplified_identification/create_application'
)


def get_previous_app_error_widget():
    return [
        {
            'description': 'Поищите ошибку в данных или напишите нам',
            'themes': {
                'dark': {
                    'background': {'color': 'FFFFEDE9'},
                    'description_text_color': 'FFFF3333',
                    'title_text_color': 'FFFF3333',
                    'delimiter_color': 'FFFF3333',
                    'button_theme': {
                        'background': {'color': 'FFFFEDE9'},
                        'text_color': 'FFFF3333',
                    },
                },
                'light': {
                    'background': {'color': 'FFFFEDE9'},
                    'description_text_color': 'FFFF3333',
                    'title_text_color': 'FFFF3333',
                    'delimiter_color': 'FFFF3333',
                    'button_theme': {
                        'background': {'color': 'FFFFEDE9'},
                        'text_color': 'FFFF3333',
                    },
                },
            },
            'title': 'Не смогли проверить паспорт',
            'button': {'text': 'В поддержку'},
        },
    ]


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
    headers = common.default_headers()
    headers.pop(header)
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=headers,
    )

    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}
    db_helpers.check_no_split_card_issue_apps(pgsql)


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize(
    'session_uuid', ['nok', 'invalid'],  # disabled in exp  # not in exp
)
async def test_user_is_not_in_exp(
        taxi_bank_applications,
        mockserver,
        bank_agreements_mock,
        blackbox_mock,
        session_uuid,
        pgsql,
):
    headers = common.default_headers()
    headers['X-YaBank-SessionUUID'] = session_uuid
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'User is not in experiment',
    }
    db_helpers.check_no_simpl_id_apps(pgsql)


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_no_last_application_ok(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        bank_forms_mock,
        pgsql,
):
    locale = 'ru'
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=common.default_headers(locale=locale),
    )
    assert response.status_code == 200

    resp_json = response.json()
    application_id = resp_json.get('application_id')

    assert len(resp_json) == 4
    assert application_id
    assert len(application_id) > 1
    assert resp_json['status'] == 'CREATED'
    assert resp_json['second_documents'] == ['INN', 'SNILS']

    db_helpers.check_asserts(
        pgsql,
        response,
        'SIMPLIFIED_IDENTIFICATION',
        bank_agreements_mock.agreements,
        bank_forms_mock.forms,
        locale=locale,
        simplified_identification_db_check=True,
    )

    app = db_helpers.get_simpl_id_app(pgsql, application_id)
    assert app.status == 'CREATED'
    assert not getattr(app, 'submit_idempotency_token')
    assert app.operation_type == 'INSERT'
    assert app.submitted_form is None
    assert app.initiator == common.INITIATOR
    assert app.user_id_type == common.USER_ID_TYPE_BUID
    assert app.user_id == common.DEFAULT_YANDEX_BUID
    assert app.reason is None
    assert app.procaas_init_idempotency_token

    history_app = db_helpers.get_simpl_id_app_hist(pgsql, application_id)
    assert history_app == app

    assert bank_agreements_mock.get_agreement_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    assert blackbox_mock.blackbox_handler.times_called == 1


async def test_no_last_application_ok_internal(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        bank_forms_mock,
        pgsql,
):
    locale = common.DEFAULT_LANGUAGE
    response = await taxi_bank_applications.post(
        INTERNAL_HANDLE,
        json={
            'yandex_uid': common.DEFAULT_YANDEX_UID,
            'yandex_buid': common.DEFAULT_YANDEX_BUID,
            'locale': locale,
            'remote_ip': common.SOME_IP,
        },
    )
    assert response.status_code == 200

    resp_json = response.json()
    application_id = resp_json.get('application_id')

    assert len(resp_json) == 4
    assert application_id
    assert len(application_id) > 1
    assert resp_json['status'] == 'CREATED'
    assert resp_json['second_documents'] == ['INN', 'SNILS']

    db_helpers.check_asserts(
        pgsql,
        response,
        'SIMPLIFIED_IDENTIFICATION',
        bank_agreements_mock.agreements,
        bank_forms_mock.forms,
        locale=locale,
        simplified_identification_db_check=True,
    )

    app = db_helpers.get_simpl_id_app(pgsql, application_id)
    assert app.status == 'CREATED'
    assert not getattr(app, 'submit_idempotency_token')
    assert app.operation_type == 'INSERT'
    assert app.submitted_form is None
    assert app.initiator == common.INITIATOR
    assert app.user_id_type == common.USER_ID_TYPE_BUID
    assert app.user_id == common.DEFAULT_YANDEX_BUID
    assert app.reason is None
    assert app.procaas_init_idempotency_token

    history_app = db_helpers.get_simpl_id_app_hist(pgsql, application_id)
    assert history_app == app

    assert bank_agreements_mock.get_agreement_handler.times_called == 0
    assert taxi_processing_mock.create_event_handler.times_called == 1
    assert blackbox_mock.blackbox_handler.times_called == 1


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.config(
    BANK_APPLICATIONS_SIMPLIFIED_IDENTIFICATION_SECOND_DOCUMENT=['INN'],
)
async def test_valid_second_document(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        bank_forms_mock,
        pgsql,
        bank_audit,
):
    locale = 'ru'
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=common.default_headers(locale=locale),
    )
    assert response.status_code == 200

    resp_json = response.json()
    # application_id = resp_json.get('application_id')

    assert len(resp_json) == 4
    assert resp_json['second_documents'] == ['INN']


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize('status_code', [400, 404, 500])
async def test_agreement_error(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        status_code,
        pgsql,
):
    bank_agreements_mock.set_http_status_code(status_code)

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE,
        headers=common.default_headers(),
        json={'type': 'SIMPLIFIED_IDENTIFICATION'},
    )

    assert response.status_code == 500
    assert taxi_processing_mock.create_event_handler.times_called == 0
    db_helpers.check_no_simpl_id_apps(pgsql)


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_procaas_error(
        taxi_bank_applications,
        bank_core_client_mock,
        bank_agreements_mock,
        blackbox_mock,
        taxi_processing_mock,
        pgsql,
):
    taxi_processing_mock.set_http_status_code(500)
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=common.default_headers(),
    )
    assert response.status_code == 500


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize('status', ['CREATED', 'PROCESSING', 'SUCCESS'])
async def test_create_application_with_last_application(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        pgsql,
        status,
):
    locale = 'ru'
    headers = common.default_headers(locale=locale)
    last_app_response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=headers,
    )
    assert last_app_response.status_code == 200

    resp_json = last_app_response.json()
    application_id = resp_json.get('application_id')
    assert resp_json['second_documents'] == ['INN', 'SNILS']
    db_helpers.update_simpl_id_app_status(pgsql, application_id, status)

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=headers,
    )

    if status == 'SUCCESS':
        assert response.status_code == 409
        assert response.json() == {
            'code': 'Conflict',
            'message': (
                'Application of this type'
                ' is already processed with SUCCESS state'
            ),
        }
    else:
        assert response.status_code == 200
        app = db_helpers.get_simpl_id_app(pgsql, application_id)
        assert app.status == 'CREATED' if status == 'CREATED' else 'PROCESSING'
        assert not getattr(app, 'submit_idempotency_token')
        assert blackbox_mock.blackbox_handler.times_called == 1
        assert taxi_processing_mock.create_event_handler.has_calls
        assert (
            taxi_processing_mock.create_event_handler.times_called == 2
            if status == 'CREATED'
            else 1
        )


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize('status', ['CREATED', 'PROCESSING', 'SUCCESS'])
async def test_create_application_internal_with_last_application(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        pgsql,
        status,
):
    body = {
        'yandex_uid': common.DEFAULT_YANDEX_UID,
        'yandex_buid': common.DEFAULT_YANDEX_BUID,
        'locale': 'ru',
        'remote_ip': common.SOME_IP,
    }
    last_app_response = await taxi_bank_applications.post(
        INTERNAL_HANDLE, json=body,
    )
    assert last_app_response.status_code == 200

    resp_json = last_app_response.json()
    application_id = resp_json.get('application_id')
    assert resp_json['second_documents'] == ['INN', 'SNILS']
    db_helpers.update_simpl_id_app_status(pgsql, application_id, status)

    response = await taxi_bank_applications.post(INTERNAL_HANDLE, json=body)

    if status == 'SUCCESS':
        assert response.status_code == 409
        assert response.json() == {
            'code': 'Conflict',
            'message': (
                'Application of this type'
                ' is already processed with SUCCESS state'
            ),
        }
    else:
        assert response.status_code == 200
        app = db_helpers.get_simpl_id_app(pgsql, application_id)
        assert app.status == 'CREATED' if status == 'CREATED' else 'PROCESSING'
        assert not getattr(app, 'submit_idempotency_token')
        assert blackbox_mock.blackbox_handler.times_called == 1
        assert taxi_processing_mock.create_event_handler.has_calls
        assert (
            taxi_processing_mock.create_event_handler.times_called == 2
            if status == 'CREATED'
            else 1
        )


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_simplified_identification_form(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        pgsql,
):
    locale = 'ru'
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=common.default_headers(locale=locale),
    )
    assert response.status_code == 200
    resp_json = response.json()
    resp_form = resp_json.get('form')
    assert resp_form == {
        'last_name': 'Петров',
        'first_name': 'Пётр',
        'birthday': '2000-07-02',
    }
    assert resp_json['second_documents'] == ['INN', 'SNILS']
    application_id = resp_json.get('application_id')
    db_form = db_helpers.get_simpl_id_draft_form(pgsql, application_id)
    assert db_form
    assert db_form.form == resp_form


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_user_with_incorrect_birthday(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        pgsql,
):
    locale = 'ru'
    headers = common.default_headers(locale=locale)
    last_app_response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=headers,
    )
    assert last_app_response.status_code == 200
    last_resp_json = last_app_response.json()
    assert last_resp_json['second_documents'] == ['INN', 'SNILS']
    application_id = last_resp_json.get('application_id')
    form = last_resp_json.get('form')
    form['birthday'] = '2000'
    form = json.dumps(form)
    db_helpers.update_simpl_id_draft_form(pgsql, form, application_id)

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=headers,
    )

    resp_form = response.json().get('form')
    assert resp_form == {
        'last_name': 'Петров',
        'first_name': 'Пётр',
        'birthday': '2000',
    }

    db_form = db_helpers.get_simpl_id_draft_form(pgsql, application_id)
    assert db_form
    assert db_form.form == resp_form


@pytest.mark.parametrize(
    'application_status, status_code',
    [('CREATED', 500), ('PROCESSING', 500), ('FAILED', 200), ('SUCCESS', 500)],
)
@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_application_not_in_simplified_identification_db(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        pgsql,
        application_status,
        bank_audit,
        status_code,
):
    locale = 'ru'
    db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'SIMPLIFIED_IDENTIFICATION',
        application_status,
        False,
    )

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=common.default_headers(locale=locale),
    )
    assert response.status_code == status_code


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_no_data_from_blackbox(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        pgsql,
):
    locale = 'ru'
    headers = common.default_headers(locale=locale)
    headers['X-Yandex-UID'] = 'bad_uid'
    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=headers,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['second_documents'] == ['INN', 'SNILS']
    assert 'form' not in resp_json


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_race_condition(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        pgsql,
        testpoint,
):
    locale = 'ru'

    @testpoint('data_race')
    async def _data_race(data):
        db_helpers.insert_simpl_application(
            pgsql,
            submitted_form=json.dumps(common.get_standard_submitted_form()),
            prenormalized_form=json.dumps(
                common.get_standard_submitted_form(),
            ),
            agreement_version=2,
            status=common.STATUS_CREATED,
        )

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=common.default_headers(locale=locale),
    )
    assert response.status_code == 500


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_last_failed_application(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        bank_forms_mock,
        pgsql,
):
    db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=json.dumps(common.get_standard_submitted_form()),
        prenormalized_form=json.dumps(common.get_standard_submitted_form()),
        agreement_version=2,
        status=common.STATUS_FAILED,
        simpl_status=common.STATUS_FAILED,
        create_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
        update_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
        submit_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
    )

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['second_documents'] == ['INN', 'SNILS']
    widgets = resp_json.get('widgets')
    assert widgets
    assert len(widgets) == 1
    assert widgets == get_previous_app_error_widget()

    form = common.get_standard_submitted_form()
    inn_or_snils = form.pop('snils')
    form['inn_or_snils'] = inn_or_snils
    resp_form = resp_json.get('form')
    assert resp_form == form


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize('status', ['CREATED', 'DRAFT_SAVED'])
async def test_two_applications_with_failed(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        blackbox_mock,
        bank_forms_mock,
        pgsql,
        status,
):
    db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=json.dumps(common.get_standard_submitted_form()),
        prenormalized_form=json.dumps(common.get_standard_submitted_form()),
        agreement_version=2,
        status=common.STATUS_FAILED,
        create_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
        update_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
        submit_idempotency_token=common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
    )

    db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=json.dumps(common.get_standard_submitted_form()),
        prenormalized_form=json.dumps(common.get_standard_submitted_form()),
        agreement_version=2,
        status=common.STATUS_CREATED,
        simpl_status=status,
    )

    response = await taxi_bank_applications.post(
        PUBLIC_HANDLE, headers=common.default_headers(),
    )

    assert response.status_code == 200
    resp_json = response.json()
    assert resp_json['second_documents'] == ['INN', 'SNILS']

    if status == common.STATUS_CREATED:
        widgets = resp_json.get('widgets')
        assert widgets
        assert len(widgets) == 1
        assert widgets == get_previous_app_error_widget()
    resp_form = resp_json.get('form')
    assert resp_form == common.get_standard_form()

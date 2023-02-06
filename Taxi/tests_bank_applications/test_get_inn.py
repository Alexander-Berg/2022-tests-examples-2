import json

import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


def get_default_request(application_id='67754336-d4d1-43c1-aadb-cabd06674ea6'):
    return {
        'last_name': 'Петров',
        'first_name': 'Пётр',
        'middle_name': 'Петрович',
        'passport_number': '6812000000',
        'birthday': '2000-07-02',
        'application_id': application_id,
    }


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn(taxi_bank_applications, nalog_ru_mock, pgsql):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    body = get_default_request(application_id)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {'inn': '000000000000'}
    assert nalog_ru_mock.get_request_id_handler.has_calls
    assert nalog_ru_mock.get_inn_handler.has_calls


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_cached(taxi_bank_applications, nalog_ru_mock, pgsql):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        prenormalized_form=json.dumps(form),
        submitted_form=json.dumps(form),
        agreement_version='0',
        simpl_status='CREATED',
        status='CREATED',
    )

    body = get_default_request(application_id)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {'inn': '000000000000'}
    assert nalog_ru_mock.get_request_id_handler.times_called == 1
    assert nalog_ru_mock.get_inn_handler.times_called == 1

    body = get_default_request(application_id)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {'inn': '000000000000'}
    assert nalog_ru_mock.get_request_id_handler.times_called == 1
    assert nalog_ru_mock.get_inn_handler.times_called == 1


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_no_application(
        taxi_bank_applications, nalog_ru_mock, pgsql,
):
    body = get_default_request()
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 404


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_failed_on_first_call(
        taxi_bank_applications, pgsql, nalog_ru_mock,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    body = get_default_request(application_id)
    nalog_ru_mock.set_get_request_response(
        400,
        {
            'ERROR': '-',
            'ERRORS': {'docno': ['some_error_text']},
            'STATUS': 400,
        },
    )
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 500
    assert nalog_ru_mock.get_request_id_handler.has_calls
    assert not nalog_ru_mock.get_inn_handler.has_calls


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_failed_on_second_call(
        taxi_bank_applications, pgsql, nalog_ru_mock,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    body = get_default_request(application_id)
    nalog_ru_mock.set_get_inn_response(400, {'ERROR': '-', 'STATUS': 400})
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 500
    assert nalog_ru_mock.get_request_id_handler.has_calls
    assert nalog_ru_mock.get_inn_handler.has_calls


@pytest.mark.parametrize(
    'state,expected_code', [(0, 404), (-1, 404), (1, 404)],
)
@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_different_states(
        taxi_bank_applications, nalog_ru_mock, pgsql, state, expected_code,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    body = get_default_request(application_id)
    nalog_ru_mock.set_get_inn_response(200, {'state': state})
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == expected_code
    assert nalog_ru_mock.get_request_id_handler.has_calls
    assert nalog_ru_mock.get_inn_handler.has_calls


@pytest.mark.parametrize(
    'body_item', ['last_name', 'first_name', 'birthday', 'passport_number'],
)
@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_without_field(
        taxi_bank_applications, nalog_ru_mock, pgsql, body_item, mockserver,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
    )

    body = get_default_request(application_id)
    del body[body_item]
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 400
    assert not nalog_ru_mock.get_request_id_handler.has_calls
    assert not nalog_ru_mock.get_inn_handler.has_calls


@pytest.mark.parametrize(
    'body_item',
    ['last_name', 'first_name', 'middle_name', 'birthday', 'passport_number'],
)
@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_with_empty_field(
        taxi_bank_applications, nalog_ru_mock, pgsql, body_item,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
    )

    body = get_default_request(application_id)
    body['last_name'] = ''
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 400
    assert not nalog_ru_mock.get_request_id_handler.has_calls
    assert not nalog_ru_mock.get_inn_handler.has_calls


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_with_invalid_birthday(
        taxi_bank_applications, nalog_ru_mock, pgsql,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
    )

    body = get_default_request(application_id)
    body['birthday'] = '02-07-2000'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 400
    assert not nalog_ru_mock.get_request_id_handler.has_calls
    assert not nalog_ru_mock.get_inn_handler.has_calls


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_with_datetime_birthday(
        taxi_bank_applications, nalog_ru_mock, pgsql,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
    )

    body = get_default_request(application_id)
    body['birthday'] = '2000-07-02T00:00:00.000+00:00'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 400
    assert not nalog_ru_mock.get_request_id_handler.has_calls
    assert not nalog_ru_mock.get_inn_handler.has_calls


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_not_found(taxi_bank_applications, nalog_ru_mock, pgsql):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    body = get_default_request(application_id)
    body['last_name'] = 'Иванов'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 404
    assert nalog_ru_mock.get_request_id_handler.has_calls
    assert nalog_ru_mock.get_inn_handler.has_calls


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_broken(taxi_bank_applications, nalog_ru_mock, pgsql):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    body = get_default_request(application_id)
    body['last_name'] = 'Сидоров'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 500
    assert nalog_ru_mock.get_request_id_handler.has_calls
    assert nalog_ru_mock.get_inn_handler.has_calls


async def test_get_inn_disabled_default(
        taxi_bank_applications, nalog_ru_mock, pgsql,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    body = get_default_request(application_id)
    body['last_name'] = 'Сидоров'
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 404
    assert not nalog_ru_mock.get_request_id_handler.has_calls
    assert not nalog_ru_mock.get_inn_handler.has_calls


@pytest.mark.parametrize(
    'field,invalid_value',
    [('first_name', ''), ('last_name', ''), ('passport_number', '1')],
)
async def test_simplified_identification_get_inn_invalid_data_in_body(
        taxi_bank_applications, nalog_ru_mock, field, invalid_value,
):
    body = get_default_request()
    body[field] = invalid_value
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 400


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_draft_exst(
        pgsql, taxi_bank_applications, nalog_ru_mock,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    body = get_default_request(application_id)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )

    assert response.status_code == 200
    assert response.json()['inn']

    body['inn_or_snils'] = response.json()['inn']
    del body['application_id']

    draft = db_helpers.get_simpl_id_draft_form(pgsql, application_id)

    assert draft is not None
    assert draft.form == body


@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_draft_conflict(
        pgsql, taxi_bank_applications, nalog_ru_mock, testpoint,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    @testpoint('insert conflict')
    def _update_current_app_status(data):
        db_helpers.update_application_status(
            pgsql, application_id, 'PROCESSING',
        )
        db_helpers.update_simpl_id_app_status(
            pgsql, application_id, 'PROCESSING',
        )

    body = get_default_request(application_id)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )

    assert response.status_code == 404


@pytest.mark.parametrize('different_form', [False, True])
@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_different_forms_or_not(
        taxi_bank_applications, nalog_ru_mock, pgsql, different_form,
):
    form = common.get_standard_normalized_form()
    form.pop('snils')
    form['inn_or_snils'] = '000000000000'
    if different_form:
        form.pop('birthday')

    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    form['application_id'] = application_id
    if different_form:
        form['birthday'] = common.BIRTHDAY

    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=form,
        headers=common.default_headers(),
    )
    assert response.status_code == 200
    assert response.json() == {'inn': '000000000000'}
    assert nalog_ru_mock.get_request_id_handler.has_calls
    assert nalog_ru_mock.get_inn_handler.has_calls

    application = db_helpers.get_simpl_id_app(pgsql, application_id)
    assert application.status == (
        'DRAFT_SAVED' if different_form else 'CREATED'
    )


@pytest.mark.parametrize(
    'responses',
    [
        [(200, {'state': -1}), (200, {'state': 0, 'inn': '000000000000'})],
        [
            (200, {'state': -1}),
            (200, {'state': -1}),
            (200, {'state': 0, 'inn': '000000000000'}),
        ],
    ],
)
@pytest.mark.config(BANK_APPLICATIONS_GET_INN_ENABLED=True)
async def test_get_inn_backoff_retries(
        taxi_bank_applications, nalog_ru_mock, pgsql, responses,
):
    form = {'some': True}
    application_id = db_helpers.insert_simpl_application(
        pgsql=pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        agreement_version='0',
        status='CREATED',
        simpl_status='CREATED',
    )

    body = get_default_request(application_id)
    nalog_ru_mock.set_get_inn_responses(responses)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/simplified_identification/get_inn',
        json=body,
        headers=common.default_headers(),
    )
    assert response.status_code == 200
    assert nalog_ru_mock.get_request_id_handler.times_called == 1
    assert nalog_ru_mock.get_inn_handler.times_called == len(responses)

import json

import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers

APPLICATION_ID = '483653cd-13bb-42d6-802e-a4b47ebfa2ca'


def add_application_default(pgsql, application_status):
    application_type = 'SIMPLIFIED_IDENTIFICATION'
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        application_type,
        'CREATED'
        if application_status in ['CREATED', 'DRAFT_SAVED']
        else 'PROCESSING',
        False,
    )
    db_helpers.add_simpl_id_application(
        pgsql, application_id, application_status,
    )
    return application_id


@pytest.mark.parametrize('application_id', ['', '111'])
async def test_bad_application_id(
        taxi_bank_applications, pgsql, application_id,
):
    headers = common.default_headers()
    body = {
        'application_id': application_id,
        'form': common.get_standard_form(),
    }
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 400


async def test_application_noexist(taxi_bank_applications, pgsql):
    headers = common.default_headers()
    body = {
        'application_id': APPLICATION_ID,
        'form': common.get_standard_form(),
    }
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'Can\'t find application data with requested id',
    }


@pytest.mark.parametrize(
    'header', ['X-Yandex-BUID', 'X-Yandex-UID', 'X-YaBank-PhoneID'],
)
@pytest.mark.parametrize('application_status', ['CREATED', 'PROCESSING'])
async def test_no_authorized(
        taxi_bank_applications, pgsql, application_status, header,
):
    headers = common.default_headers()
    headers.pop(header)
    application_id = add_application_default(pgsql, application_status)
    body = {
        'application_id': application_id,
        'form': common.get_standard_form(),
    }
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}


@pytest.mark.parametrize('application_status', ['CREATED', 'DRAFT_SAVED'])
async def test_simple(taxi_bank_applications, pgsql, application_status):
    headers = common.default_headers()
    application_id = add_application_default(pgsql, application_status)
    body = {
        'application_id': application_id,
        'form': common.get_standard_form(),
    }

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200

    pg_result = db_helpers.get_simpl_id_draft_forms(pgsql, application_id)

    assert len(pg_result) == 1
    db_form = db_helpers.SimplifiedIdentificationDraftForm(
        *(pg_result[0]),
    ).form
    assert db_form == common.get_standard_form()


@pytest.mark.parametrize('application_status', ['CREATED', 'DRAFT_SAVED'])
async def test_two_forms(taxi_bank_applications, pgsql, application_status):
    headers = common.default_headers()
    application_id = add_application_default(pgsql, application_status)
    body = {
        'application_id': application_id,
        'form': common.get_standard_form(),
    }

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200

    pg_result = db_helpers.get_simpl_id_draft_forms(pgsql, application_id)

    assert len(pg_result) == 1

    body['form']['last_name'] = 'Иванов'
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200

    pg_result = db_helpers.get_simpl_id_draft_forms(pgsql, application_id)
    assert len(pg_result) == 2

    form = common.get_standard_form()
    db_form = db_helpers.SimplifiedIdentificationDraftForm(
        *(pg_result[1]),
    ).form
    assert db_form == form

    form['last_name'] = 'Иванов'
    db_form_latest = db_helpers.SimplifiedIdentificationDraftForm(
        *(pg_result[0]),
    ).form
    assert db_form_latest == form


@pytest.mark.parametrize('application_status', ['CREATED', 'DRAFT_SAVED'])
async def test_invalid_passport_number(
        taxi_bank_applications, pgsql, application_status,
):
    headers = common.default_headers()
    application_id = add_application_default(pgsql, application_status)
    body = {
        'application_id': application_id,
        'form': common.get_standard_form(),
    }
    body['form']['password'] = '123'

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('application_status', ['CREATED', 'DRAFT_SAVED'])
async def test_invalid_date_of_birth(
        taxi_bank_applications, pgsql, application_status,
):
    headers = common.default_headers()
    application_id = add_application_default(pgsql, application_status)
    body = {
        'application_id': application_id,
        'form': common.get_standard_form(),
    }
    body['form']['birthday'] = '02-07-2000'
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.parametrize('application_status', ['CREATED', 'DRAFT_SAVED'])
async def test_invalid_inn(taxi_bank_applications, pgsql, application_status):
    headers = common.default_headers()
    application_id = add_application_default(pgsql, application_status)
    body = {
        'application_id': application_id,
        'form': common.get_standard_form(),
    }
    body['form']['inn_or_snils'] = '1234'
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'field',
    [
        'first_name',
        'middle_name',
        'passport_number',
        'birthday',
        'inn_or_snils',
    ],
)
@pytest.mark.parametrize('application_status', ['CREATED', 'DRAFT_SAVED'])
async def test_not_full_form(
        taxi_bank_applications, pgsql, application_status, field,
):
    headers = common.default_headers()
    application_id = add_application_default(pgsql, application_status)
    form = common.get_standard_form()
    form.pop(field)
    body = {'application_id': application_id, 'form': form}

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200

    pg_result = db_helpers.get_simpl_id_draft_forms(pgsql, application_id)

    assert len(pg_result) == 1
    db_form = db_helpers.SimplifiedIdentificationDraftForm(
        *(pg_result[0]),
    ).form
    assert db_form == form


@pytest.mark.parametrize(
    'application_status',
    [
        'SUBMITTED',
        'PROCESSING',
        'AGREEMENTS_ACCEPTED',
        'CORE_BANKING',
        'SUCCESS',
        'FAILED',
    ],
)
async def test_invalid_status(
        taxi_bank_applications, pgsql, application_status,
):
    headers = common.default_headers()
    application_id = add_application_default(pgsql, application_status)
    body = {
        'application_id': application_id,
        'form': common.get_standard_form(),
    }
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 409


@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
@pytest.mark.parametrize('application_status', ['CREATED', 'DRAFT_SAVED'])
async def test_client_status_after_set_form(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        pgsql,
        application_status,
):
    headers = common.default_headers()
    application_id = add_application_default(pgsql, application_status)
    body = {
        'application_id': application_id,
        'form': common.get_standard_form(),
    }
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json=body,
        headers=headers,
    )
    assert response.status_code == 200

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/create_application',
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json().get('status') == 'CREATED'


@pytest.mark.parametrize('different_form', [False, True])
@pytest.mark.experiments3(
    filename='bank_simplified_identification_feature_experiments.json',
)
async def test_set_draft_form_for_created_app_with_different_forms(
        taxi_bank_applications,
        bank_agreements_mock,
        taxi_processing_mock,
        pgsql,
        different_form,
):
    form = common.get_standard_normalized_form()
    form.pop('snils')
    if different_form:
        form.pop('birthday')

    application_id = db_helpers.insert_simpl_application(
        pgsql,
        submitted_form=json.dumps(form),
        prenormalized_form=json.dumps(form),
        status='CREATED',
        simpl_status='CREATED',
    )

    if different_form:
        form['birthday'] = common.BIRTHDAY

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/set_draft_form',
        json={'application_id': application_id, 'form': form},
        headers=common.default_headers(),
    )

    assert response.status_code == 200
    application = db_helpers.get_simpl_id_app(pgsql, application_id)
    assert application.status == (
        'DRAFT_SAVED' if different_form else 'CREATED'
    )

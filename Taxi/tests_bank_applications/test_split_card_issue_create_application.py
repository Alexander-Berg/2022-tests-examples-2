import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


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
        'v1/applications/v1/split_card_issue/create_application',
        headers=headers,
    )

    assert response.status_code == 401
    assert response.json() == {'code': '401', 'message': 'Unauthorized'}
    db_helpers.check_no_split_card_issue_apps(pgsql)


@pytest.mark.experiments3(filename='bank_split_card_feature_experiments.json')
@pytest.mark.parametrize(
    'session_uuid', ['nok', 'invalid'],  # disabled in exp  # not in exp
)
async def test_user_is_not_in_exp(
        taxi_bank_applications, mockserver, session_uuid, pgsql,
):
    headers = common.default_headers()
    headers['X-YaBank-SessionUUID'] = session_uuid
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/create_application',
        headers=headers,
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'User is not in experiment',
    }
    db_helpers.check_no_split_card_issue_apps(pgsql)


@pytest.mark.experiments3(filename='bank_split_card_feature_experiments.json')
@pytest.mark.parametrize('status_code', [404, 500])
async def test_client_info_error(
        taxi_bank_applications,
        mockserver,
        bank_core_client_mock,
        pgsql,
        status_code,
):
    bank_core_client_mock.set_http_status_code(status_code)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/create_application',
        headers=common.default_headers(),
    )
    assert response.status_code == 500
    db_helpers.check_no_split_card_issue_apps(pgsql)


@pytest.mark.experiments3(filename='bank_split_card_feature_experiments.json')
@pytest.mark.parametrize('auth_level', ['ANONYMOUS', 'IDENTIFIED'])
async def test_user_is_not_kyc(
        taxi_bank_applications,
        mockserver,
        bank_core_client_mock,
        pgsql,
        auth_level,
):
    bank_core_client_mock.set_auth_level(auth_level)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/create_application',
        headers=common.default_headers(),
    )
    assert response.status_code == 404
    assert response.json() == {
        'code': 'NotFound',
        'message': 'User is not KYC',
    }
    db_helpers.check_no_split_card_issue_apps(pgsql)


@pytest.mark.experiments3(filename='bank_split_card_feature_experiments.json')
@pytest.mark.parametrize('status_code', [400, 404, 500])
async def test_agreement_error(
        taxi_bank_applications,
        mockserver,
        bank_core_client_mock,
        bank_agreements_mock,
        pgsql,
        status_code,
):
    bank_agreements_mock.set_http_status_code(status_code)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/create_application',
        headers=common.default_headers(),
    )
    assert response.status_code == 500
    db_helpers.check_no_split_card_issue_apps(pgsql)


@pytest.mark.experiments3(filename='bank_split_card_feature_experiments.json')
@pytest.mark.parametrize(
    'locale,agreement',
    [
        ('ru', 'Это карта сплита'),
        ('en', 'This is split card'),
        ('invlalid', 'Это карта сплита'),
    ],
)
async def test_agreement_locales(
        taxi_bank_applications,
        mockserver,
        bank_core_client_mock,
        bank_agreements_mock,
        taxi_processing_mock,
        locale,
        agreement,
):
    headers = common.default_headers()
    headers['X-Request-Language'] = locale
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/create_application',
        headers=headers,
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert 'application_id' in resp_json
    assert resp_json['agreement'] == agreement


@pytest.mark.experiments3(filename='bank_split_card_feature_experiments.json')
async def test_procaas_error(
        taxi_bank_applications,
        mockserver,
        bank_core_client_mock,
        bank_agreements_mock,
        taxi_processing_mock,
        pgsql,
):
    taxi_processing_mock.set_http_status_code(500)
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/create_application',
        headers=common.default_headers(),
    )
    assert response.status_code == 500


@pytest.mark.experiments3(filename='bank_split_card_feature_experiments.json')
async def test_ok_simple(
        taxi_bank_applications,
        mockserver,
        bank_core_client_mock,
        bank_agreements_mock,
        taxi_processing_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/create_application',
        headers=common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json) == 3
    application_id = resp_json.get('application_id')
    assert application_id
    assert len(application_id) > 1
    assert resp_json['status'] == 'CREATED'
    assert resp_json['agreement'] == 'Это карта сплита'
    db_helpers.check_asserts(
        pgsql,
        response,
        'SPLIT_CARD_ISSUE',
        bank_agreements_mock.agreements,
        forms=None,
    )
    assert taxi_processing_mock.create_event_handler.times_called == 1

    app = db_helpers.get_split_card_issue_app(pgsql, application_id)
    assert app.status == 'CREATED'
    assert not getattr(app, 'submit_idempotency_token')
    assert app.operation_type == 'INSERT'

    history_app = db_helpers.get_split_card_issue_app_hist(
        pgsql, application_id,
    )
    assert history_app == app


@pytest.mark.experiments3(filename='bank_split_card_feature_experiments.json')
async def test_ok_with_retry(
        taxi_bank_applications,
        mockserver,
        bank_core_client_mock,
        bank_agreements_mock,
        taxi_processing_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/create_application',
        headers=common.default_headers(),
    )
    assert response.status_code == 200
    resp_json = response.json()
    assert len(resp_json) == 3
    assert resp_json['status'] == 'CREATED'
    application_id = resp_json.get('application_id')
    assert len(application_id) > 1
    agreement = resp_json['agreement']
    assert agreement == 'Это карта сплита'
    db_helpers.check_asserts(
        pgsql,
        response,
        'SPLIT_CARD_ISSUE',
        bank_agreements_mock.agreements,
        forms=None,
    )

    response2 = await taxi_bank_applications.post(
        'v1/applications/v1/split_card_issue/create_application',
        headers=common.default_headers(),
    )
    assert response2.status_code == 200
    resp_json2 = response2.json()
    assert resp_json2 == {
        'application_id': application_id,
        'agreement': agreement,
        'status': 'CREATED',
    }
    db_helpers.check_asserts(
        pgsql,
        response,
        'SPLIT_CARD_ISSUE',
        bank_agreements_mock.agreements,
        forms=None,
    )
    assert taxi_processing_mock.create_event_handler.times_called == 2

    app = db_helpers.get_split_card_issue_app(pgsql, application_id)
    assert app.status == 'CREATED'
    assert not getattr(app, 'submit_idempotency_token')
    assert app.operation_type == 'INSERT'

    history_app = db_helpers.get_split_card_issue_app_hist(
        pgsql, application_id,
    )
    assert history_app == app

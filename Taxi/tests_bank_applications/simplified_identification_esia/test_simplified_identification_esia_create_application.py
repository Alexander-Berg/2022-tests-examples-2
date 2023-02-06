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
async def test_simplified_identification_esia_create_app_unauthorized(
        taxi_bank_applications,
        core_esia_integration_mock,
        pgsql,
        taxi_processing_mock,
        header,
):
    headers = common.default_headers()
    headers.pop(header)
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=headers,
    )

    assert response.status_code == 401


async def test_simplified_identification_esia_user_no_exp(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 404
    assert (
        not core_esia_integration_mock.esia_create_application_handler.has_calls  # noqa
    )
    assert not taxi_processing_mock.create_event_handler.has_calls


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
@pytest.mark.parametrize(
    'session_uuid', ['nok', 'invalid'],  # disabled in exp  # not in exp
)
async def test_simplified_identification_esia_user_not_in_exp(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        session_uuid,
):
    headers = common.default_headers()
    headers['X-YaBank-SessionUUID'] = session_uuid

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=headers,
    )

    assert response.status_code == 404
    assert (
        not core_esia_integration_mock.esia_create_application_handler.has_calls  # noqa
    )
    assert not taxi_processing_mock.create_event_handler.has_calls


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
async def test_simplified_identification_esia_create_app_esia_integration_500(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    core_esia_integration_mock.internal_error = True

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 500
    assert core_esia_integration_mock.esia_create_application_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
async def test_simplified_identification_esia_create_app_no_previous_app(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 200
    assert core_esia_integration_mock.esia_create_application_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    applications = db_helpers.select_simpl_esia_apps(
        pgsql, common.DEFAULT_YANDEX_BUID,
    )
    assert len(applications) == 1
    assert applications[0].esia_state == 'abc'
    assert applications[0].redirect_url == ''
    assert applications[0].application_id == response.json()['application_id']

    application_history = db_helpers.select_simpl_esia_apps_hist(
        pgsql, applications[0].application_id,
    )
    assert len(application_history) == 2


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
@pytest.mark.config(BANK_APPLICATIONS_ESIA_REDIRECT_URI='1234')
async def test_simplified_identification_esia_create_app_check_config(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    core_esia_integration_mock.check_redirect_uri = '1234'

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 200
    assert core_esia_integration_mock.esia_create_application_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    applications = db_helpers.select_simpl_esia_apps(
        pgsql, common.DEFAULT_YANDEX_BUID,
    )
    assert len(applications) == 1
    assert applications[0].esia_state == 'abc'
    assert applications[0].redirect_url == '1234'
    assert applications[0].application_id == response.json()['application_id']

    application_history = db_helpers.select_simpl_esia_apps_hist(
        pgsql, applications[0].application_id,
    )
    assert len(application_history) == 2


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
@pytest.mark.parametrize('esia_state', [None, 'not_null_esia_state'])
async def test_simplified_identification_esia_create_app_old_created_app(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        esia_state,
):
    buid = common.DEFAULT_YANDEX_BUID
    old_application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CREATED,
        simpl_esia_status=common.STATUS_CREATED,
        esia_state=esia_state,
        redirect_url=(None if esia_state is None else '4321'),
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 200
    assert core_esia_integration_mock.esia_create_application_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    applications = db_helpers.select_simpl_esia_apps(pgsql, buid)
    assert len(applications) == 1
    assert applications[0].application_id == old_application_id
    assert response.json()['application_id'] == old_application_id

    application_history = db_helpers.select_simpl_esia_apps_hist(
        pgsql, applications[0].application_id,
    )

    if esia_state is None:
        assert applications[0].esia_state == 'abc'
        assert applications[0].redirect_url == ''
        assert len(application_history) == 1
    else:
        assert applications[0].esia_state == esia_state
        assert applications[0].redirect_url == '4321'
        assert not application_history


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
@pytest.mark.parametrize(
    'status',
    [
        common.STATUS_SUBMITTED,
        common.STATUS_PROCESSING,
        common.STATUS_CORE_BANKING,
        common.STATUS_SUCCESS,
    ],
)
async def test_simplified_identification_esia_create_app_bad_old_app_status(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        status,
):
    old_status = (
        common.STATUS_SUCCESS
        if status == common.STATUS_SUCCESS
        else common.STATUS_PROCESSING
    )
    old_application_id = db_helpers.insert_simpl_esia_application(
        pgsql, status=old_status, simpl_esia_status=status,
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 409
    assert 'message' in response.json()
    assert (
        response.json()['message']
        == f'There is application in {status} status application_id({old_application_id})'  # noqa
    )

    applications = db_helpers.select_simpl_esia_apps(
        pgsql, common.DEFAULT_YANDEX_BUID,
    )
    assert len(applications) == 1


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
async def test_simplified_identification_esia_create_app_prev_status_failed(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    old_application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_FAILED,
        simpl_esia_status=common.STATUS_FAILED,
    )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 200
    assert core_esia_integration_mock.esia_create_application_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    applications = db_helpers.select_simpl_esia_apps(
        pgsql, common.DEFAULT_YANDEX_BUID,
    )

    assert len(applications) == 2
    assert applications[0].application_id == old_application_id
    assert applications[0].status == common.STATUS_FAILED
    assert applications[1].esia_state == 'abc'
    assert applications[1].redirect_url == ''
    assert applications[1].application_id != old_application_id
    assert applications[1].application_id == response.json()['application_id']

    application_history = db_helpers.select_simpl_esia_apps_hist(
        pgsql, applications[1].application_id,
    )
    assert len(application_history) == 2


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
async def test_simplified_identification_esia_create_app_old_app_changed(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        testpoint,
):
    buid = common.DEFAULT_YANDEX_BUID
    old_application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CREATED,
        simpl_esia_status=common.STATUS_CREATED,
    )

    @testpoint('esia_application_update')
    async def _data_race(data):
        db_helpers.update_simpl_esia_id_app_status(
            pgsql, old_application_id, common.STATUS_PROCESSING,
        )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 500
    assert core_esia_integration_mock.esia_create_application_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls

    applications = db_helpers.select_simpl_esia_apps(pgsql, buid)
    assert len(applications) == 1
    assert applications[0].application_id == old_application_id
    assert applications[0].esia_state is None
    assert applications[0].redirect_url is None


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
async def test_simplified_identification_esia_create_app_race_insert_new_app(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        testpoint,
):
    buid = common.DEFAULT_YANDEX_BUID

    @testpoint('esia_application_insert')
    async def _data_race(data):
        db_helpers.insert_simpl_esia_application(
            pgsql,
            status=common.STATUS_CREATED,
            simpl_esia_status=common.STATUS_CREATED,
        )

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 500
    assert (
        not core_esia_integration_mock.esia_create_application_handler.has_calls  # noqa
    )
    assert not taxi_processing_mock.create_event_handler.has_calls

    applications = db_helpers.select_simpl_esia_apps(pgsql, buid)
    assert len(applications) == 1
    assert applications[0].esia_state is None
    assert applications[0].redirect_url is None


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
async def test_simplified_identification_esia_state_changed_during_handling(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
        testpoint,
):
    buid = common.DEFAULT_YANDEX_BUID
    esia_state = 'not_null_esia_state'
    old_application_id = db_helpers.insert_simpl_esia_application(
        pgsql,
        status=common.STATUS_CREATED,
        simpl_esia_status=common.STATUS_CREATED,
    )

    @testpoint('esia_application_update')
    async def _data_race(data):
        sql = """
            UPDATE bank_applications.simplified_identification_esia
            SET esia_state = %s
            WHERE application_id = %s
            RETURNING application_id;
        """
        cursor = pgsql['bank_applications'].cursor()
        cursor.execute(sql, [esia_state, old_application_id])
        records = cursor.fetchall()
        assert len(records) == 1

    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 500
    assert core_esia_integration_mock.esia_create_application_handler.has_calls
    assert not taxi_processing_mock.create_event_handler.has_calls

    applications = db_helpers.select_simpl_esia_apps(pgsql, buid)
    assert len(applications) == 1
    assert applications[0].application_id == old_application_id
    assert applications[0].esia_state == esia_state
    assert applications[0].redirect_url is None


@pytest.mark.experiments3(filename='bank_kyc_eds_feature_experiments.json')
async def test_simplified_identification_esia_create_app_processing_500(
        taxi_bank_applications,
        core_esia_integration_mock,
        taxi_processing_mock,
        pgsql,
):
    taxi_processing_mock.http_status_code = 500
    response = await taxi_bank_applications.post(
        '/v1/applications/v1/simplified_identification/esia/create_application',  # noqa
        headers=common.default_headers(),
    )

    assert response.status_code == 500
    assert core_esia_integration_mock.esia_create_application_handler.has_calls
    assert taxi_processing_mock.create_event_handler.has_calls

    applications = db_helpers.select_simpl_esia_apps(
        pgsql, common.DEFAULT_YANDEX_BUID,
    )
    assert len(applications) == 1
    assert applications[0].esia_state == 'abc'
    assert applications[0].redirect_url == ''

    application_history = db_helpers.select_simpl_esia_apps_hist(
        pgsql, applications[0].application_id,
    )
    assert len(application_history) == 2

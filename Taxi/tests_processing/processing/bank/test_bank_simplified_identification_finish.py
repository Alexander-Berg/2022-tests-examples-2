import pytest

from tests_processing.processing.bank import common


@pytest.mark.parametrize(
    'status, expected_notification_tries, expected_delete_tries',
    [('success', 1, 1), ('failed', 1, 0), ('wrong', 0, 0)],
)
async def test_bank_simplified_finish_notification(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        status,
        expected_notification_tries,
        expected_delete_tries,
):
    helper = common.SimplHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    application_status = common.STATUS_SUCCESS
    if status == 'failed':
        application_status = common.STATUS_FAILED
        defaults_groups = [common.FAILED_DEFAULTS_GROUP]
    elif status == 'success':
        defaults_groups = [common.SUCCESS_DEFAULTS_GROUP]
    elif status == 'wrong':
        defaults_groups = 'wrong!!!'
        application_status = 'wrong!!!'
    else:
        defaults_groups = [common.SUCCESS_DEFAULTS_GROUP]
    helper.set_values(defaults_groups=defaults_groups)
    await helper.create_simpl_application()
    helper.prepare_mocks()
    await helper.send_simplified_finish_event(
        application_status=application_status,
    )
    helper.check_finish_calls(
        notifications_sended=expected_notification_tries,
        delete_pd_sended=expected_delete_tries,
    )


@pytest.mark.parametrize(
    'error, expected_notification_tries',
    [('first_fail', 2), ('first_timeout', 2)],
)
async def test_bank_simplified_finish_failed(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error,
        expected_notification_tries,
):
    helper = common.SimplHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    if error == 'first_fail':
        notifications_mock.send_notification.first_fail = True
    elif error == 'first_timeout':
        notifications_mock.send_notification.first_timeout = True
    helper.set_values(defaults_groups=[common.SUCCESS_DEFAULTS_GROUP])
    await helper.create_simpl_application()
    helper.prepare_mocks()
    await helper.send_simplified_finish_event()
    helper.check_finish_calls(
        notifications_sended=expected_notification_tries, delete_pd_sended=1,
    )


@pytest.mark.config(
    BANK_APPLICATIONS_SIMPLIFIED_IDENTIFICATION_NOTIFICATION_PROCESSING_ENABLED=False,  # noqa
)
@pytest.mark.config(
    BANK_APPLICATIONS_SIMPLIFIED_IDENTIFICATION_NOTIFICATION_FAILED_ENABLED=False,  # noqa
)
@pytest.mark.config(
    BANK_APPLICATIONS_SIMPLIFIED_IDENTIFICATION_NOTIFICATION_SUCCESS_ENABLED=False,  # noqa
)
@pytest.mark.parametrize('status', ['success', 'failed', 'wrong'])
async def test_bank_simplified_finish_disable_notification(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        status,
):
    helper = common.SimplHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    application_status = common.STATUS_SUCCESS
    if status == 'failed':
        application_status = common.STATUS_FAILED
        defaults_groups = [
            common.PROGRESS_DEFAULTS_GROUP,
            common.FAILED_DEFAULTS_GROUP,
        ]
    elif status == 'success':
        defaults_groups = common.SUCCESS_DEFAULTS_GROUPS_LIST
    elif status == 'wrong':
        defaults_groups = 'wrong!!!'
        application_status = 'wrong!!!'
    else:
        defaults_groups = common.SUCCESS_DEFAULTS_GROUPS_LIST
    helper.set_values(defaults_groups=defaults_groups)
    await helper.create_simpl_application()
    helper.prepare_mocks()
    await helper.send_simplified_finish_event(
        application_status=application_status,
    )
    helper.check_finish_calls(
        notifications_sended=0,
        delete_pd_sended=1 if status == 'success' else 0,
    )


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {'application_status': common.STATUS_SUCCESS},
            'none',
            {'application_status': common.STATUS_SUCCESS, 'is_error': False},
            1,
        ),
        (
            {'application_status': common.STATUS_FAILED},
            'fail_status',
            {'application_status': common.STATUS_FAILED},
            0,
        ),
        (
            {'application_status': None},
            'null',
            {'application_status': None},
            0,
        ),
        (
            {'application_status': common.STATUS_SUCCESS},
            'one_fail',
            {'application_status': common.STATUS_SUCCESS, 'is_error': False},
            2,
        ),
        (
            {'application_status': common.STATUS_SUCCESS},
            'one_timeout',
            {'application_status': common.STATUS_SUCCESS, 'is_error': False},
            2,
        ),
    ],
)
async def test_bank_simpl_stage_delete_pd_stage(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        started_shared,
        error_type,
        expected_shared,
        expected_tries,
):
    helper = common.SimplHelper(
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        processing,
    )
    helper.set_values()
    await helper.create_simpl_application()
    helper.prepare_mocks()
    if error_type == 'one_fail':
        applications_mock.delete_personal_data.first_fail = True
    elif error_type == 'one_timeout':
        applications_mock.delete_personal_data.first_timeout = True
    await helper.start_single_stage(
        'delete-personal-data-stage-stage-id', started_shared, expected_shared,
    )
    helper.check_delete_pd_calls(delete_data=expected_tries)

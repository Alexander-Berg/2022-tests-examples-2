import pytest

from tests_processing.processing.bank import common


@pytest.mark.parametrize(
    'started_shared, error_type, expected_shared, expected_tries',
    [
        (
            {
                'agreement_version': common.AGREEMENT_VERSION,
                'application_type': 'SIMPLIFIED_IDENTIFICATION',
                'config': {'accept_agreement_stage': {'enabled': True}},
            },
            'none',
            {
                'agreement_version': common.AGREEMENT_VERSION,
                'application_type': 'SIMPLIFIED_IDENTIFICATION',
                'application_status': common.STATUS_AGREMENTS_ACCEPTED,
                'is_error': False,
                'errors': None,
                'config': {'accept_agreement_stage': {'enabled': True}},
            },
            1,
        ),
        (
            {
                'agreement_version': common.AGREEMENT_VERSION,
                'application_type': 'SIMPLIFIED_IDENTIFICATION',
                'config': {'accept_agreement_stage': {'enabled': True}},
            },
            'one_fail',
            {
                'agreement_version': common.AGREEMENT_VERSION,
                'application_type': 'SIMPLIFIED_IDENTIFICATION',
                'application_status': common.STATUS_AGREMENTS_ACCEPTED,
                'is_error': False,
                'errors': None,
                'config': {'accept_agreement_stage': {'enabled': True}},
            },
            2,
        ),
        (
            {
                'agreement_version': common.AGREEMENT_VERSION,
                'application_type': 'SIMPLIFIED_IDENTIFICATION',
                'config': {'accept_agreement_stage': {'enabled': True}},
            },
            'one_timeout',
            {
                'agreement_version': common.AGREEMENT_VERSION,
                'application_type': 'SIMPLIFIED_IDENTIFICATION',
                'application_status': common.STATUS_AGREMENTS_ACCEPTED,
                'is_error': False,
                'errors': None,
                'config': {'accept_agreement_stage': {'enabled': True}},
            },
            2,
        ),
    ],
)
async def test_bank_simpl_stage_accept_agreement(
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
        agreements_mock.accept_agreement.first_fail = True
    elif error_type == 'one_timeout':
        agreements_mock.accept_agreement.first_timeout = True
    await helper.start_single_stage(
        'accept-agreement-stage-id',
        started_shared,
        expected_shared=expected_shared,
    )


@pytest.mark.parametrize(
    'error_code, expected_tries, stq_fail, ', [(400, 1, True), (500, 3, True)],
)
async def test_bank_simpl_get_application_data_response_error(
        processing,
        mockserver,
        passport_mock,
        core_client_mock,
        userinfo_mock,
        applications_mock,
        processing_mock,
        notifications_mock,
        agreements_mock,
        error_code,
        expected_tries,
        stq_fail,
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
    agreements_mock.accept_agreement.response_code = error_code

    await helper.send_simpl_event(stq_fail=stq_fail)
    helper.check_simpl_calls(
        notifications_sended=1,
        accept_agreement=expected_tries,
        simpl_get_application_data=1,
    )

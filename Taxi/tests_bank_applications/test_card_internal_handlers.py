import pytest

from tests_bank_applications import common
from tests_bank_applications import db_helpers


async def test_card_internal_submit_application(
        taxi_bank_applications, mockserver, taxi_processing_mock, pgsql,
):
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'DIGITAL_CARD_ISSUE',
        'CREATED',
        multiple_success_status_allowed=True,
    )
    response = await taxi_bank_applications.post(
        'card-internal/v1/submit',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': application_id,
            'agreement_id': 'test-agreement-id',
        },
    )

    assert response.status_code == 200
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'PROCESSING'
    assert taxi_processing_mock.create_event_handler.times_called == 1


async def test_card_internal_submit_pass_agreement_id_to_procaas(
        taxi_bank_applications, mockserver, pgsql,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        application_type,
        'CREATED',
        multiple_success_status_allowed=True,
    )

    agreement_id = 'test-agreement-id'

    @mockserver.json_handler('/processing/v1/bank/applications/create-event')
    def _create_event_handler(request):
        assert request.headers['X-Idempotency-Token']
        if 'session_uuid' in request.json:
            session_uuid = request.json.pop('session_uuid')
            assert session_uuid == common.DEFAULT_YABANK_SESSION_UUID
        assert request.json == {
            'kind': 'update',
            'type': application_type,
            'buid': common.DEFAULT_YANDEX_BUID,
            'agreement_id': agreement_id,
        }
        return {'event_id': 'event_id'}

    response = await taxi_bank_applications.post(
        'card-internal/v1/submit',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
            'application_id': application_id,
            'agreement_id': agreement_id,
        },
    )
    assert response.status_code == 200
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'PROCESSING'


@pytest.mark.parametrize('application_status', ['PROCESSING', 'SUCCESS'])
async def test_card_internal_submit_has_other_processing_application(
        taxi_bank_applications,
        application_status,
        mockserver,
        taxi_processing_mock,
        pgsql,
):
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'DIGITAL_CARD_ISSUE',
        'CREATED',
        multiple_success_status_allowed=True,
    )
    # other application that already in status PROCESSING or SUCCESS
    db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'DIGITAL_CARD_ISSUE',
        application_status,
        multiple_success_status_allowed=True,
        create_idempotency_token='5768BEFB-ACD2-41EF-8E7B-5593C779EEE3',
    )
    response = await taxi_bank_applications.post(
        'card-internal/v1/submit',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
            'application_id': application_id,
            'agreement_id': 'test-agreement-id',
        },
    )

    assert response.status_code == 200
    assert taxi_processing_mock.create_event_handler.times_called == 1


async def test_card_internal_submit_invalid_application_id(
        taxi_bank_applications, mockserver, taxi_processing_mock, pgsql,
):
    response = await taxi_bank_applications.post(
        'v1/applications/v1/submit_form',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'application_id': '1-2-3-4-5',
            'agreement_id': 'test-agreement-id',
        },
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'update_token,submit_token,code,procaas_times_called',
    [
        (None, common.DEFAULT_IDEMPOTENCY_TOKEN, 200, 1),
        (
            common.DEFAULT_IDEMPOTENCY_TOKEN,
            common.DEFAULT_IDEMPOTENCY_TOKEN,
            200,
            1,
        ),
        (
            common.DEFAULT_IDEMPOTENCY_TOKEN,
            'ec838cfc-f44b-4674-9c0a-0d0c87e011f2',
            409,
            0,
        ),
    ],
)
async def test_card_internal_double_submit_application_in_processing_status(
        taxi_bank_applications,
        mockserver,
        taxi_processing_mock,
        pgsql,
        update_token,
        submit_token,
        code,
        procaas_times_called,
):
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'DIGITAL_CARD_ISSUE',
        'PROCESSING',
        multiple_success_status_allowed=True,
        update_idempotency_token=update_token,
    )

    response = await taxi_bank_applications.post(
        'card-internal/v1/submit',
        headers={'X-Idempotency-Token': submit_token},
        json={
            'buid': common.DEFAULT_YANDEX_BUID,
            'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
            'application_id': application_id,
            'agreement_id': 'test-agreement-id',
        },
    )
    assert response.status_code == code
    assert (
        taxi_processing_mock.create_event_handler.times_called
        == procaas_times_called
    )

    sql = """
        SELECT status, update_idempotency_token
        FROM bank_applications.applications
        WHERE application_id = %s
    """
    cursor = pgsql['bank_applications'].cursor()
    cursor.execute(sql, [application_id])
    records = cursor.fetchall()
    assert len(records) == 1
    assert records[0] == ('PROCESSING', update_token)


async def test_card_internal_submit_permission_violation(
        taxi_bank_applications, mockserver, taxi_processing_mock, pgsql,
):
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        'DIGITAL_CARD_ISSUE',
        'CREATED',
        multiple_success_status_allowed=True,
    )

    response = await taxi_bank_applications.post(
        'card-internal/v1/submit',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={
            'buid': common.TEST_ONE_YANDEX_BUID,
            'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
            'application_id': application_id,
            'agreement_id': 'test-agreement-id',
        },
    )

    assert response.status_code == 404


async def test_card_internal_create_application(
        taxi_bank_applications,
        pgsql,
        mockserver,
        bank_agreements_mock,
        taxi_processing_mock,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    response = await taxi_bank_applications.post(
        'card-internal/v1/create_application',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={'buid': common.DEFAULT_YANDEX_BUID, 'type': application_type},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'CREATED'
    db_helpers.check_asserts(
        pgsql, response, application_type, agreements=None, forms=None,
    )


@pytest.mark.parametrize(
    'application_status', ['CREATED', 'PROCESSING', 'FAILED', 'SUCCESS'],
)
async def test_card_internal_create_application_new_idempotency_token(
        taxi_bank_applications,
        pgsql,
        application_status,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        application_type,
        application_status,
        True,
    )

    response = await taxi_bank_applications.post(
        'card-internal/v1/create_application',
        headers={
            'X-Idempotency-Token': '67754336-d4d1-43c1-aadb-cabd06674ea7',
        },
        json={'buid': common.DEFAULT_YANDEX_BUID, 'type': application_type},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'CREATED'
    assert application_id != response.json()['application_id']


@pytest.mark.parametrize('application_status', ['CREATED', 'PROCESSING'])
async def test_card_internal_create_application_old_idempotency_token(
        taxi_bank_applications,
        pgsql,
        application_status,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        application_type,
        application_status,
        True,
    )

    response = await taxi_bank_applications.post(
        'card-internal/v1/create_application',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={'buid': common.DEFAULT_YANDEX_BUID, 'type': application_type},
    )
    assert response.status_code == 200
    assert response.json()['status'] == application_status
    assert application_id == response.json()['application_id']


async def test_card_internal_create_application_old_idemp_token_failed_status(
        taxi_bank_applications,
        pgsql,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        application_type,
        'FAILED',
        True,
        create_idempotency_token='5768BEFB-ACD2-41EF-8E7B-5593C779EEE3',
    )

    response = await taxi_bank_applications.post(
        'card-internal/v1/create_application',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={'buid': common.DEFAULT_YANDEX_BUID, 'type': application_type},
    )
    assert response.status_code == 200
    assert response.json()['status'] == 'CREATED'
    assert application_id != response.json()['application_id']


async def test_card_internal_create_application_old_idemp_token_success_status(
        taxi_bank_applications,
        pgsql,
        mockserver,
        taxi_processing_mock,
        bank_agreements_mock,
):
    application_type = 'DIGITAL_CARD_ISSUE'
    db_helpers.add_application(
        pgsql,
        'BUID',
        common.DEFAULT_YANDEX_BUID,
        application_type,
        'SUCCESS',
        True,
    )

    response = await taxi_bank_applications.post(
        'card-internal/v1/create_application',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json={'buid': common.DEFAULT_YANDEX_BUID, 'type': application_type},
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    'buid,product,card_type',
    [
        (common.DEFAULT_YANDEX_BUID, 'WALLET', 'DIGITAL'),
        ('fc597589-ca10-48f4-9e52-6c042496eb6c', 'WALLET', 'MIR_DIGITAL'),
        ('2abed4c7-5835-4f19-92a0-a19de9256f9f', 'WALLET', None),
        (common.DEFAULT_YANDEX_BUID, 'PRO', 'MC_YANDEX_PRO'),
        ('fc597589-ca10-48f4-9e52-6c042496eb6c', 'PRO', 'MIR_YANDEX_PRO'),
        ('2abed4c7-5835-4f19-92a0-a19de9256f9f', 'PRO', 'MC_YANDEX_PRO'),
    ],
)
@pytest.mark.experiments3(filename='bank_digital_card_type.json')
async def test_card_internal_submit_card_type_from_exp(
        taxi_bank_applications, mockserver, pgsql, buid, product, card_type,
):
    application_id = db_helpers.add_application(
        pgsql,
        'BUID',
        buid,
        'DIGITAL_CARD_ISSUE',
        'CREATED',
        multiple_success_status_allowed=True,
    )
    agreement_id = 'test-agreement-id'

    @mockserver.json_handler('/processing/v1/bank/applications/create-event')
    def _create_event_handler(request):
        assert request.headers['X-Idempotency-Token']
        if card_type is not None:
            card_type_value = request.json.pop('card_type')
            assert card_type_value == card_type
        else:
            assert 'card_type' not in request.json
        assert request.json == {
            'kind': 'update',
            'type': 'DIGITAL_CARD_ISSUE',
            'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
            'buid': buid,
            'agreement_id': agreement_id,
        }
        return {'event_id': 'event_id'}

    body = {
        'buid': buid,
        'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
        'application_id': application_id,
        'agreement_id': agreement_id,
    }
    if product is not None:
        body['product'] = product
    response = await taxi_bank_applications.post(
        '/card-internal/v1/submit',
        headers={'X-Idempotency-Token': common.DEFAULT_IDEMPOTENCY_TOKEN},
        json=body,
    )
    assert response.status_code == 200
    application = db_helpers.get_application(pgsql, application_id)
    assert application.status == 'PROCESSING'

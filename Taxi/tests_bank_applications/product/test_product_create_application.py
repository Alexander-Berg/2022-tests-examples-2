import pytest

from tests_bank_applications import common
from tests_bank_applications.product import db_helpers

MOCK_NOW = '2021-09-28T19:31:00+00:00'
HANDLE_URL = '/v1/applications/v1/product/create_application'


def check_asserts(pgsql, response, agreements, product, locale='ru'):
    application_type = 'PRODUCT'
    if locale in ('ru', 'unknown'):
        assert (
            response['agreement']
            == agreements['ru'][application_type]['agreement_text']
        )
    elif locale == 'en':
        assert (
            response['agreement']
            == agreements['en'][application_type]['agreement_text']
        )
    assert response['status'] == common.STATUS_PROCESSING

    application_id = response['application_id']
    application = db_helpers.select_application(pgsql, application_id)

    assert application.buid == common.DEFAULT_YANDEX_BUID
    assert application.status == common.STATUS_SUBMITTED
    assert application.product == product
    assert not application.multiple_success_status_allowed
    assert application.agreement_version == 0
    assert application.initiator == {
        'initiator_type': 'BUID',
        'initiator_id': common.DEFAULT_YANDEX_BUID,
    }


@pytest.mark.parametrize(
    'product', [common.PRODUCT_WALLET, common.PRODUCT_PRO],
)
async def test_ok(
        taxi_bank_applications,
        pgsql,
        bank_agreements_mock,
        taxi_processing_mock,
        product,
):
    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )

    assert response.status_code == 200
    check_asserts(
        pgsql, response.json(), bank_agreements_mock.agreements, product,
    )

    assert bank_agreements_mock.get_agreement_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    call = taxi_processing_mock.create_event_handler.next_call()
    assert (
        call['request'].headers['X-Idempotency-Token']
        == common.DEFAULT_IDEMPOTENCY_TOKEN
    )
    assert call['request'].json == {
        'kind': 'run',
        'type': 'PRODUCT',
        'product': product,
        'yuid': common.DEFAULT_YANDEX_UID,
        'buid': common.DEFAULT_YANDEX_BUID,
        'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
        'client_ip': common.SOME_IP,
        'agreement_version': bank_agreements_mock.agreements['ru']['PRODUCT'][
            'version'
        ],
    }


async def test_with_no_agreement_in_config(
        taxi_bank_applications, bank_agreements_mock,
):
    product = common.PRODUCT_WALLET
    bank_agreements_mock.set_agreements({})
    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.headers_with_idempotency(),
        json={'product': product},
    )

    assert response.status_code == 500
    assert bank_agreements_mock.get_agreement_handler.times_called == 1


async def test_already_created(
        taxi_bank_applications,
        pgsql,
        bank_agreements_mock,
        taxi_processing_mock,
):
    product = common.PRODUCT_WALLET
    application_id = db_helpers.insert_application(pgsql)
    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )

    assert response.status_code == 200
    assert response.json()['application_id'] == application_id

    check_asserts(
        pgsql, response.json(), bank_agreements_mock.agreements, product,
    )

    assert bank_agreements_mock.get_agreement_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    call = taxi_processing_mock.create_event_handler.next_call()
    assert (
        call['request'].headers['X-Idempotency-Token']
        == common.DEFAULT_IDEMPOTENCY_TOKEN
    )
    assert call['request'].json == {
        'kind': 'run',
        'type': 'PRODUCT',
        'product': product,
        'yuid': common.DEFAULT_YANDEX_UID,
        'buid': common.DEFAULT_YANDEX_BUID,
        'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
        'client_ip': common.SOME_IP,
        'agreement_version': bank_agreements_mock.agreements['ru']['PRODUCT'][
            'version'
        ],
    }


async def test_already_submitted(
        taxi_bank_applications,
        pgsql,
        bank_agreements_mock,
        taxi_processing_mock,
):
    product = common.PRODUCT_WALLET
    application_id = db_helpers.insert_application(pgsql)
    db_helpers.update_status_and_idempotency(
        pgsql,
        application_id,
        common.STATUS_SUBMITTED,
        common.DEFAULT_IDEMPOTENCY_TOKEN,
    )

    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )

    assert response.status_code == 200
    assert response.json()['application_id'] == application_id

    check_asserts(
        pgsql, response.json(), bank_agreements_mock.agreements, product,
    )

    assert bank_agreements_mock.get_agreement_handler.times_called == 1
    assert taxi_processing_mock.create_event_handler.times_called == 1
    call = taxi_processing_mock.create_event_handler.next_call()
    assert (
        call['request'].headers['X-Idempotency-Token']
        == common.DEFAULT_IDEMPOTENCY_TOKEN
    )
    assert call['request'].json == {
        'kind': 'run',
        'type': 'PRODUCT',
        'product': product,
        'yuid': common.DEFAULT_YANDEX_UID,
        'buid': common.DEFAULT_YANDEX_BUID,
        'session_uuid': common.DEFAULT_YABANK_SESSION_UUID,
        'client_ip': common.SOME_IP,
        'agreement_version': bank_agreements_mock.agreements['ru']['PRODUCT'][
            'version'
        ],
    }


async def test_already_processing(
        taxi_bank_applications, pgsql, bank_agreements_mock,
):
    product = common.PRODUCT_WALLET
    application_id = db_helpers.insert_application(pgsql)
    db_helpers.update_status_and_idempotency(
        pgsql,
        application_id,
        common.STATUS_PROCESSING,
        common.DEFAULT_IDEMPOTENCY_TOKEN,
    )

    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )

    assert response.status_code == 200
    assert response.json()['application_id'] == application_id

    assert bank_agreements_mock.get_agreement_handler.times_called == 1


async def test_idempotency_one(
        taxi_bank_applications,
        pgsql,
        bank_agreements_mock,
        taxi_processing_mock,
):
    product = common.PRODUCT_WALLET
    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']
    assert response.json()['status'] == common.STATUS_PROCESSING
    assert taxi_processing_mock.create_event_handler.times_called == 1

    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )
    assert response.status_code == 200
    assert response.json()['application_id'] == application_id
    assert response.json()['status'] == common.STATUS_PROCESSING
    assert taxi_processing_mock.create_event_handler.times_called == 2

    db_helpers.update_status(pgsql, application_id, common.STATUS_PROCESSING)
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )
    assert response.status_code == 200
    assert response.json()['application_id'] == application_id
    assert response.json()['status'] == common.STATUS_PROCESSING
    assert taxi_processing_mock.create_event_handler.times_called == 2

    db_helpers.update_status(pgsql, application_id, common.STATUS_SUCCESS)
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )
    assert response.status_code == 200
    assert response.json()['application_id'] == application_id
    assert taxi_processing_mock.create_event_handler.times_called == 2

    db_helpers.update_status(pgsql, application_id, common.STATUS_FAILED)
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )
    assert response.status_code == 200
    assert response.json()['application_id'] == application_id
    assert response.json()['status'] == common.STATUS_FAILED
    assert taxi_processing_mock.create_event_handler.times_called == 2


async def test_with_previous_failed(
        taxi_bank_applications,
        pgsql,
        bank_agreements_mock,
        taxi_processing_mock,
):
    product = common.PRODUCT_WALLET
    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )
    assert response.status_code == 200
    application_id = response.json()['application_id']
    assert taxi_processing_mock.create_event_handler.times_called == 1
    call = taxi_processing_mock.create_event_handler.next_call()
    assert (
        call['request'].headers['X-Idempotency-Token']
        == common.DEFAULT_IDEMPOTENCY_TOKEN
    )

    db_helpers.update_status(pgsql, application_id, common.STATUS_FAILED)
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )
    assert response.status_code == 200
    assert response.json()['application_id'] == application_id
    assert response.json()['status'] == common.STATUS_FAILED
    assert taxi_processing_mock.create_event_handler.times_called == 0

    response = await taxi_bank_applications.post(
        HANDLE_URL,
        headers=common.headers_with_idempotency(
            common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
        ),
        json={'product': product},
    )
    assert response.status_code == 200
    assert response.json()['application_id'] != application_id
    check_asserts(
        pgsql, response.json(), bank_agreements_mock.agreements, product,
    )
    assert taxi_processing_mock.create_event_handler.times_called == 1
    call = taxi_processing_mock.create_event_handler.next_call()
    assert (
        call['request'].headers['X-Idempotency-Token']
        == common.NOT_DEFAULT_IDEMPOTENCY_TOKEN
    )


async def test_history_table(
        taxi_bank_applications,
        pgsql,
        taxi_processing_mock,
        bank_agreements_mock,
):
    product = common.PRODUCT_WALLET
    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )

    assert response.status_code == 200
    application_id = response.json()['application_id']

    record = db_helpers.select_application(pgsql, application_id)
    records_history = db_helpers.select_applications_history(
        pgsql, application_id,
    )
    assert len(records_history) == 1
    assert record == records_history[0]


async def test_processing_has_fall_double(
        taxi_bank_applications,
        pgsql,
        bank_agreements_mock,
        taxi_processing_mock,
):
    taxi_processing_mock.set_http_status_code(500)
    taxi_processing_mock.set_response({})
    product = common.PRODUCT_WALLET
    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )
    assert response.status_code == 500
    # default retry count
    assert taxi_processing_mock.create_event_handler.times_called == 3
    assert bank_agreements_mock.get_agreement_handler.times_called == 1

    taxi_processing_mock.create_event_handler.flush()
    bank_agreements_mock.get_agreement_handler.flush()
    taxi_processing_mock.set_http_status_code(200)
    taxi_processing_mock.set_response({'event_id': 'abc123'})
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )
    assert response.status_code == 200
    check_asserts(
        pgsql, response.json(), bank_agreements_mock.agreements, product,
    )
    assert taxi_processing_mock.create_event_handler.times_called == 1
    assert bank_agreements_mock.get_agreement_handler.times_called == 1


async def test_insert_conflict(
        taxi_bank_applications, pgsql, bank_agreements_mock, testpoint,
):
    @testpoint('insert_conflict')
    def _insert_same_applicaton(data):
        db_helpers.insert_application(pgsql, status=common.STATUS_SUCCESS)

    product = common.PRODUCT_WALLET
    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )

    assert response.status_code == 500


async def test_409(taxi_bank_applications, pgsql, bank_agreements_mock):
    product = common.PRODUCT_WALLET
    application_id = db_helpers.insert_application(pgsql, product=product)
    db_helpers.update_status_and_idempotency(
        pgsql,
        application_id,
        common.STATUS_SUCCESS,
        common.NOT_DEFAULT_IDEMPOTENCY_TOKEN,
    )

    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': product},
    )

    assert response.status_code == 409


async def test_with_other_product(
        taxi_bank_applications, taxi_processing_mock, bank_agreements_mock,
):
    headers = common.headers_with_idempotency()
    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': common.PRODUCT_WALLET},
    )
    assert response.status_code == 200
    first_application_id = response.json()['application_id']

    response = await taxi_bank_applications.post(
        HANDLE_URL, headers=headers, json={'product': common.PRODUCT_PRO},
    )
    assert response.status_code == 200
    second_application_id = response.json()['application_id']

    assert first_application_id != second_application_id

import pytest

from tests_scooters_payments import consts


@pytest.mark.parametrize(
    'invoice_retrieve_resp_json, invoice_retrieve_status, expected_status, expected_body',
    [
        pytest.param('invoice_retrieve_held.json', 200, 200, {}, id='held'),
        pytest.param(
            'invoice_retrieve_holding.json',
            200,
            402,
            {
                'error_details': {
                    'special_info': {
                        'error_code': 'required_deposit_is_not_held',
                    },
                },
            },
            id='holding',
        ),
        pytest.param(
            'invoice_retrieve_not_found.json',
            404,
            404,
            {'code': 'not-found', 'message': 'Invoice not found'},
            id='not_found',
        ),
    ],
)
@pytest.mark.experiments3(filename='exp3_scooters_payments_config.json')
async def test_payments_check(
        taxi_scooters_payments,
        mockserver,
        load_json,
        invoice_retrieve_resp_json,
        invoice_retrieve_status,
        expected_status,
        expected_body,
):
    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def invoice_retrieve(request):
        assert request.json == load_json(
            'invoice_retrieve_expected_request.json',
        )
        return mockserver.make_response(
            status=invoice_retrieve_status,
            json=load_json(invoice_retrieve_resp_json),
        )

    response = await taxi_scooters_payments.get(
        '/scooters-payments/v1/payments/check',
        headers=consts.AUTH_HEADERS,
        params={'session_id': 'SESSION_ID'},
    )

    assert response.status_code == expected_status
    assert response.json() == expected_body

    assert invoice_retrieve.times_called == 1


@pytest.mark.parametrize(
    'max_processing_time, expected_status, expected_body',
    [
        pytest.param(60, 200, {}, id='max processing time'),
        pytest.param(
            None,
            402,
            {
                'error_details': {
                    'special_info': {
                        'error_code': 'required_deposit_is_not_held',
                    },
                },
            },
            id='no max processing time',
        ),
    ],
)
@pytest.mark.parametrize(
    'invoice_retrieve_resp_json',
    [
        pytest.param('invoice_retrieve_holding.json', id='holding'),
        pytest.param('invoice_retrieve_init.json', id='init'),
    ],
)
async def test_max_processing_time(
        taxi_scooters_payments,
        taxi_scooters_payments_monitor,
        mockserver,
        load_json,
        max_processing_time,
        expected_status,
        expected_body,
        invoice_retrieve_resp_json,
        experiments3,
        mocked_time,
):
    config = load_json('exp3_scooters_payments_config.json')['configs'][0]
    config['default_value'][
        'consider_successful_after_processing_seconds'
    ] = max_processing_time
    experiments3.add_config(**config)

    @mockserver.json_handler('/transactions-ng/v2/invoice/retrieve')
    def invoice_retrieve(request):
        assert request.json == load_json(
            'invoice_retrieve_expected_request.json',
        )
        return load_json(invoice_retrieve_resp_json)

    response = await taxi_scooters_payments.get(
        '/scooters-payments/v1/payments/check',
        headers=consts.AUTH_HEADERS,
        params={'session_id': 'SESSION_ID'},
    )

    assert response.status_code == expected_status
    assert response.json() == expected_body

    assert invoice_retrieve.times_called == 1

    if response.status_code == 402:
        return

    mocked_time.sleep(5)
    await taxi_scooters_payments.tests_control(invalidate_caches=False)

    metrics = await taxi_scooters_payments_monitor.get_metric(
        'scooters_payments_metrics',
    )
    assert metrics == {'skipped_payments': 1}

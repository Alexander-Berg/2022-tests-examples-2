import itertools

import pytest

from billing_fin_payouts.generated.cron import run_cron


@pytest.mark.now('2022-06-03T09:00:00.000000+03:00')
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_GET_BANK_STATEMENTS_ENABLED=True,
    BILLING_FIN_PAYOUTS_GET_BANK_STATEMENTS_SETTINGS={
        'account_ids': ['account_id_1'],
        'start_since': '2022-06-02',
        'yt_clusters': ['hahn'],
        'yt_path': 'features/billing-fin-payouts/bank-statements',
        'upload_to_yt_chunk': 1000,
        'upload_to_yt_timeout_ms': 5000,
    },
    BILLING_FIN_PAYOUTS_PUBLIC_KEYS={
        'ya_bank_statements': [
            {
                'algorithm': 'RS256',
                'public_key': 'some_key',
                'expiration_time': '2099-01-01T00:00:00+00:00',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'test_data_json',
    [
        'start_from_default.json',
        'start_from_cursor.json',
        'upload_to_yt.json',
        'upload_to_yt_empty_statement.json',
        'skip_if_too_early.json',
        'do_not_upload_to_yt_already_exist.json',
        'move_to_next_date.json',
    ],
    ids=[
        'request_and_poll_from_default_date',
        'request_and_poll_from_cursor',
        'validate_and_upload_to_yt',
        'validate_and_upload_header_only',
        'do_not_request_statement_if_day_is_not_over_msk',
        'do_not_upload_if_already_exist',
        'move_to_next_date',
    ],
)
async def test_get_bank_statements(
        test_data_json, load_json, patch, mock_yt_client, mockserver,
):
    test_data = load_json(test_data_json)
    created_yt_clients = []

    # pylint: disable=unused-variable
    @patch('billing_fin_payouts.utils.yt.get_custom_yt_client')
    def get_custom_yt_client(context, cluster):
        result = mock_yt_client(cluster, nodes=test_data['existing_nodes'])
        nonlocal created_yt_clients
        created_yt_clients.append(result)
        return result

    # pylint: disable=unused-variable
    @patch('jwt.encode')
    def _do_not_encode_jwt(payload, *args, **kwargs) -> bytes:
        return str(payload).encode()

    # pylint: disable=unused-variable
    @patch('jwt.decode')
    def _do_not_decode_jwt(payload, *args, **kwargs):
        return test_data['jwt_responses'][payload]

    @mockserver.json_handler('/bank-h2h/h2h/v1/order_statement')
    async def _h2h_order_statement(request):
        assert request.json == test_data['expected_order_statement_request']
        return mockserver.make_response(
            **test_data['order_statement_response'],
        )

    @mockserver.json_handler('/bank-h2h/h2h/v1/get_statement_status')
    async def _h2h_statement_status(request):
        assert request.json == test_data['expected_statement_status_request']
        return mockserver.make_response(
            **test_data['statement_status_response'],
        )

    @mockserver.json_handler('/bank-h2h/h2h/v1/get_statement_file')
    async def _h2h_statement_file(request):
        return mockserver.make_response(
            response=test_data['statement_file'].encode(),
            content_type='application/octet-stream',
            status=200,
        )

    await run_cron.main(
        ['billing_fin_payouts.crontasks.get_bank_statements', '-t', '0'],
    )

    assert len(created_yt_clients) == 1

    yt_client = created_yt_clients[0]

    created_tables = [
        {'path': path, 'schema': schema}
        for path, schema in zip(
            yt_client.create_calls, yt_client.create_schemas,
        )
    ]

    assert created_tables == test_data['expected_created_yt_tables']
    _cmp_upload_data(
        yt_client.write_table_calls, test_data['expected_uploaded_data'],
    )
    assert yt_client.exists_calls == test_data['expected_exists_calls']
    assert yt_client.mkdir_calls == test_data['expected_mkdir_calls']
    assert yt_client.set_calls == test_data['expected_set_calls']
    assert yt_client.get_calls == test_data['expected_get_calls']
    assert yt_client.lock_calls == test_data['expected_lock_calls']


@pytest.mark.now('2022-06-03T09:00:00.000000+03:00')
@pytest.mark.config(
    BILLING_FIN_PAYOUTS_GET_BANK_STATEMENTS_ENABLED=True,
    BILLING_FIN_PAYOUTS_GET_BANK_STATEMENTS_SETTINGS={
        'account_ids': ['account_id_1'],
        'start_since': '2022-06-01',
        'yt_clusters': ['hahn'],
        'yt_path': 'features/billing-fin-payouts/bank-statements',
        'upload_to_yt_chunk': 1000,
        'upload_to_yt_timeout_ms': 5000,
    },
    BILLING_FIN_PAYOUTS_PUBLIC_KEYS={
        'ya_bank_statements': [
            {
                'algorithm': 'RS256',
                'public_key': 'some_key',
                'expiration_time': '2099-01-01T00:00:00+00:00',
            },
        ],
    },
)
@pytest.mark.parametrize(
    'test_data_json',
    [
        'check_sum_mismatch.json',
        'validate_statement_row.json',
        'validate_header.json',
        pytest.param(
            'public_key_expired.json',
            marks=[
                pytest.mark.config(
                    BILLING_FIN_PAYOUTS_PUBLIC_KEYS={
                        'ya_bank_statements': [
                            {
                                'algorithm': 'RS256',
                                'public_key': 'some_key',
                                'expiration_time': '2009-01-01T00:00:00+00:00',
                            },
                        ],
                    },
                ),
            ],
        ),
    ],
    ids=[
        'check_sum_mismatch',
        'validate_statement_row',
        'validate_header',
        'public_key_expired',
    ],
)
async def test_get_bank_statements_fail(
        test_data_json, load_json, patch, mock_yt_client, mockserver,
):
    test_data = load_json(test_data_json)
    created_yt_clients = []

    # pylint: disable=unused-variable
    @patch('billing_fin_payouts.utils.yt.get_custom_yt_client')
    def get_custom_yt_client(context, cluster):
        result = mock_yt_client(cluster, nodes=test_data['existing_nodes'])
        nonlocal created_yt_clients
        created_yt_clients.append(result)
        return result

    # pylint: disable=unused-variable
    @patch('jwt.encode')
    def _do_not_encode_jwt(payload, *args, **kwargs) -> bytes:
        return str(payload).encode()

    @mockserver.json_handler('/bank-h2h/h2h/v1/order_statement')
    async def _h2h_order_statement(request):
        assert request.json == test_data['expected_order_statement_request']
        return mockserver.make_response(
            **test_data['order_statement_response'],
        )

    @mockserver.json_handler('/bank-h2h/h2h/v1/get_statement_status')
    async def _h2h_statement_status(request):
        assert request.json == test_data['expected_statement_status_request']
        return mockserver.make_response(
            **test_data['statement_status_response'],
        )

    @mockserver.json_handler('/bank-h2h/h2h/v1/get_statement_file')
    async def _h2h_statement_file(request):
        return mockserver.make_response(
            response=test_data['statement_file'].encode(),
            content_type='application/octet-stream',
            status=200,
        )

    @patch('billing_fin_payouts.crontasks.get_bank_statements._report_errors')
    def handle_error(errors):
        assert len(errors) == len(test_data['expected_error_messages'])
        for actual, expected in zip(
                errors, test_data['expected_error_messages'],
        ):
            assert actual.startswith(expected)

    await run_cron.main(
        ['billing_fin_payouts.crontasks.get_bank_statements', '-t', '0'],
    )

    assert len(created_yt_clients) == 1

    yt_client = created_yt_clients[0]

    created_tables = [
        {'path': path, 'schema': schema}
        for path, schema in zip(
            yt_client.create_calls, yt_client.create_schemas,
        )
    ]

    assert created_tables == test_data['expected_created_yt_tables']
    _cmp_upload_data(
        yt_client.write_table_calls, test_data['expected_uploaded_data'],
    )
    assert yt_client.exists_calls == test_data['expected_exists_calls']
    assert yt_client.mkdir_calls == test_data['expected_mkdir_calls']
    assert yt_client.set_calls == test_data['expected_set_calls']
    assert yt_client.get_calls == test_data['expected_get_calls']
    assert yt_client.lock_calls == test_data['expected_lock_calls']


def _cmp_upload_data(actual, expected):
    for actual_key, expected_key in itertools.zip_longest(
            sorted(actual), sorted(expected),
    ):
        assert actual_key == expected_key
        assert actual[actual_key] == expected[expected_key]

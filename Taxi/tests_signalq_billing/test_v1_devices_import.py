import pytest

ENDPOINT = '/internal-admin/signalq-billing/v1/devices/import'

ERR_RESPONSE1 = (
    'CSV parsing failed: Header field mismatch: \'op1\'!=\'opportunity_id\''
)
ERR_RESPONSE9 = (
    'Count of (adding serial_numbers + existing in db) is greater than '
    'Salesforce devices count'
)


EXPECTED_PG_SF_OPS1 = [
    ('op1', False, 'dbid1', None, 23, 10, None, '2021-12-06T03:00:00+03:00'),
    ('op2', True, None, 'tin2', 12, 22, None, '2021-12-09T03:00:00+03:00'),
]

EXPECTED_PG_BILLING_DEVICES1 = [
    ('op2', 'AAADEFabcdef2'),
    ('op2', 'AAADEFabcdef4'),
    ('op1', 'BBBDEFabcdef4'),
]


def _check_sf_ops(pgsql, expected_pg_sf_ops):
    db = pgsql['signalq_billing'].cursor()
    db.execute(
        """
        SELECT
            opportunity_id,
            is_b2b,
            park_id,
            tin,
            devices_count,
            non_paid_period_days,
            cancelled_at,
            close_datetime
        FROM signalq_billing.salesforce_opportunities
        ORDER BY opportunity_id ASC;
        """,
    )
    db_result = list(db)
    for i, db_row in enumerate(db_result):
        assert db_row[:7] == expected_pg_sf_ops[i][:7]
        assert db_row[-1].isoformat() == expected_pg_sf_ops[i][-1]


def _check_billing_devices(pgsql, expected_pg_billing_devices):
    db = pgsql['signalq_billing'].cursor()
    db.execute(
        """
        SELECT
            opportunity_id,
            serial_number
        FROM signalq_billing.billing_devices
        ORDER BY serial_number ASC;
        """,
    )
    assert list(db) == expected_pg_billing_devices


@pytest.mark.now('2021-12-12T00:00:00+03:00')
@pytest.mark.parametrize(
    'csv, expected_auth_token, query_response_path, '
    'expected_pg_sf_ops, expected_pg_billing_devices',
    [
        pytest.param(
            '200_1.csv',
            'Bearer ACCESS_TOKEN_2',
            'query_response2.json',
            EXPECTED_PG_SF_OPS1,
            EXPECTED_PG_BILLING_DEVICES1,
            marks=pytest.mark.pgsql('signalq_billing', files=['devices2.sql']),
        ),
        pytest.param(
            '200_1.csv',
            'Bearer ACCESS_TOKEN_2',
            'query_response2.json',
            EXPECTED_PG_SF_OPS1,
            EXPECTED_PG_BILLING_DEVICES1,
            marks=pytest.mark.pgsql('signalq_billing', files=['devices3.sql']),
        ),
    ],
)
async def test_v1_devices_import_200(
        taxi_signalq_billing,
        salesforce,
        load,
        load_json,
        pgsql,
        csv,
        expected_auth_token,
        query_response_path,
        expected_pg_sf_ops,
        expected_pg_billing_devices,
):
    salesforce.set_query_response(load_json(query_response_path))
    salesforce.set_query_expected_auth(expected_auth_token)

    response = await taxi_signalq_billing.post(
        ENDPOINT, data=load(csv), headers={'Content-type': 'text/csv'},
    )

    assert response.status_code == 200
    _check_sf_ops(pgsql, expected_pg_sf_ops)
    _check_billing_devices(pgsql, expected_pg_billing_devices)


@pytest.mark.pgsql('signalq_billing', files=['devices.sql'])
@pytest.mark.parametrize(
    'csv, expected_err_response',
    [
        ('400_1.csv', {'code': 'invalid_csv', 'message': ERR_RESPONSE1}),
        (
            '400_2.csv',
            {
                'code': 'invalid_csv',
                'message': (
                    'CSV parsing failed: CSV column number mismatch: 3 != 2'
                ),
            },
        ),
        (
            '400_3.csv',
            {
                'code': 'duplicating_serials',
                'message': 'Serial numbers duplicates',
                'bad_serial_numbers': ['ABCDEFabcdef2'],
            },
        ),
        (
            '400_4.csv',
            {
                'code': 'invalid_csv',
                'message': 'CSV parsing failed: Empty CSV',
            },
        ),
        (
            '400_5.csv',
            {
                'code': 'invalid_serials',
                'message': 'Bad serial numbers provided',
                'bad_serial_numbers': ['ABCDEFtbcdef2'],
            },
        ),
        (
            '400_6.csv',
            {
                'code': 'invalid_serials',
                'message': 'Bad serial numbers provided',
                'bad_serial_numbers': ['ABCDEF123456'],
            },
        ),
        (
            '400_7.csv',
            {
                'code': 'invalid_csv',
                'message': 'CSV parsing failed: Unterminated escape sentence',
            },
        ),
        (
            '400_8.csv',
            {
                'code': 'duplicating_serials',
                'message': 'Serial numbers duplicates',
                'bad_serial_numbers': ['ABCDEFabcdef2'],
            },
        ),
        (
            '400_9.csv',
            {
                'code': 'bad_devices_count',
                'message': ERR_RESPONSE9,
                'bad_opportunity_ids': ['op1'],
            },
        ),
        (
            '400_10.csv',
            {
                'code': 'binded_to_other_opportunity',
                'message': (
                    'Some serial_numbers are binded to different opportunities'
                ),
                'bad_serial_numbers': ['ABCDEFabcdef2', 'ABCDEFabcdef9'],
            },
        ),
    ],
)
async def test_v1_devices_import_without_sf_400(
        taxi_signalq_billing, load, csv, expected_err_response,
):
    response = await taxi_signalq_billing.post(
        ENDPOINT, data=load(csv), headers={'Content-type': 'text/csv'},
    )
    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == expected_err_response['code']
    assert response_json['message'] == expected_err_response['message']

    if expected_err_response.get('bad_serial_numbers') is not None:
        assert sorted(response_json['bad_serial_numbers']) == sorted(
            expected_err_response['bad_serial_numbers'],
        )

    if expected_err_response.get('bad_opportunity_ids') is not None:
        assert sorted(response_json['bad_opportunity_ids']) == sorted(
            expected_err_response['bad_opportunity_ids'],
        )


@pytest.mark.now('2021-12-12T00:00:00+03:00')
@pytest.mark.pgsql('signalq_billing', files=['devices.sql'])
@pytest.mark.parametrize(
    'csv, is_query_first_respone_401, expected_auth_token, '
    'query_response_path, expected_err_response',
    [
        (
            '400_11.csv',
            False,
            'Bearer ACCESS_TOKEN_2',
            None,
            {
                'code': 'bad_opportunity',
                'message': (
                    'There is no info in Salesforce for opportunity: op2'
                ),
            },
        ),
        (
            '400_11.csv',
            False,
            'Bearer ACCESS_TOKEN_2',
            'query_response1.json',
            {
                'code': 'bad_opportunity',
                'message': (
                    'There is no info in Salesforce for opportunity: op2'
                ),
            },
        ),
    ],
)
async def test_v1_devices_import_with_sf_400(
        taxi_signalq_billing,
        salesforce,
        load,
        load_json,
        csv,
        is_query_first_respone_401,
        expected_auth_token,
        query_response_path,
        expected_err_response,
):
    if is_query_first_respone_401:
        salesforce.set_first_query_response_401()

    if query_response_path is not None:
        salesforce.set_query_response(load_json(query_response_path))
    if expected_auth_token is not None:
        salesforce.set_query_expected_auth(expected_auth_token)

    response = await taxi_signalq_billing.post(
        ENDPOINT, data=load(csv), headers={'Content-type': 'text/csv'},
    )

    assert response.status_code == 400
    response_json = response.json()
    assert response_json['code'] == expected_err_response['code']
    assert response_json['message'] == expected_err_response['message']

    if expected_err_response.get('bad_serial_numbers') is not None:
        assert sorted(response_json['bad_serial_numbers']) == sorted(
            expected_err_response['bad_serial_numbers'],
        )

    if expected_err_response.get('bad_opportunity_ids') is not None:
        assert sorted(response_json['bad_opportunity_ids']) == sorted(
            expected_err_response['bad_opportunity_ids'],
        )

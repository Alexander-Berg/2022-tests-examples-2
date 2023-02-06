import dateutil
import pytest


@pytest.mark.now('2022-01-01T12:00:00.000000+03:00')
async def test_report(stq_runner, mock_api, load, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_traffic_fines_bank_client_report.call(
        task_id='1',
        args=(),
        kwargs={
            'initial_payment_number': 1,
            'park_id': 'PARK-ID-01',
            'query': {},
        },
    )

    assert (
        mock_api['fleet-reports-storage']['/internal/v1/file/upload']
        .next_call()['request']
        .get_data()
        .decode('cp1251')
        .replace('\r\n', '\n')
        == load('fines_bank_client.txt')
    )
    assert pg_dump() == {
        **pg_initial,
        'load_operations': {
            **pg_initial['load_operations'],
            '1': (None, 'complete'),
        },
        'park_fines': {
            **pg_initial['park_fines'],
            ('FINE_UIN_01', 'CAR_ID_01', 'PARK-ID-01'): (
                'paid',
                dateutil.parser.parse('2022-01-01T00:00:00+00:00'),
                True,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                None,
            ),
            ('FINE_UIN_02', 'CAR_ID_02', 'PARK-ID-01'): (
                'issued',
                dateutil.parser.parse('2021-12-31T00:00:00+00:00'),
                True,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T03:00:00+03:00'),
                None,
            ),
        },
    }


@pytest.mark.now('2022-01-01T12:00:00.000000+03:00')
async def test_report_only_include(stq_runner, mock_api, load, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_traffic_fines_bank_client_report.call(
        task_id='1',
        args=(),
        kwargs={
            'initial_payment_number': 1,
            'park_id': 'PARK-ID-01',
            'query': {'included_uins': ['FINE_UIN_02']},
        },
    )

    assert (
        mock_api['fleet-reports-storage']['/internal/v1/file/upload']
        .next_call()['request']
        .get_data()
        .decode('cp1251')
        .replace('\r\n', '\n')
        == load('fines_bank_client2.txt')
    )
    assert pg_dump() == {
        **pg_initial,
        'load_operations': {
            **pg_initial['load_operations'],
            '1': (None, 'complete'),
        },
        'park_fines': {
            **pg_initial['park_fines'],
            ('FINE_UIN_02', 'CAR_ID_02', 'PARK-ID-01'): (
                'issued',
                dateutil.parser.parse('2021-12-31T00:00:00+00:00'),
                True,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T03:00:00+03:00'),
                None,
            ),
        },
    }


@pytest.mark.now('2022-01-01T12:00:00.000000+03:00')
async def test_report_exclude(stq_runner, mock_api, load, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_traffic_fines_bank_client_report.call(
        task_id='1',
        args=(),
        kwargs={
            'initial_payment_number': 1,
            'park_id': 'PARK-ID-01',
            'query': {'excluded_uins': ['FINE_UIN_01']},
        },
    )

    assert (
        mock_api['fleet-reports-storage']['/internal/v1/file/upload']
        .next_call()['request']
        .get_data()
        .decode('cp1251')
        .replace('\r\n', '\n')
        == load('fines_bank_client2.txt')
    )
    assert pg_dump() == {
        **pg_initial,
        'load_operations': {
            **pg_initial['load_operations'],
            '1': (None, 'complete'),
        },
        'park_fines': {
            **pg_initial['park_fines'],
            ('FINE_UIN_02', 'CAR_ID_02', 'PARK-ID-01'): (
                'issued',
                dateutil.parser.parse('2021-12-31T00:00:00+00:00'),
                True,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T03:00:00+03:00'),
                None,
            ),
        },
    }


@pytest.mark.now('2022-01-01T12:00:00.000000+03:00')
async def test_cursor(stq_runner, mock_api, load, pg_dump):
    pg_initial = pg_dump()

    await stq_runner.fleet_traffic_fines_bank_client_report.call(
        task_id='1',
        args=(),
        kwargs={
            'initial_payment_number': 1,
            'park_id': 'PARK-ID-01',
            'query': {
                'cursor': (
                    'eyJsb2FkZWRfYXQiOiIyMDIyLTAxLTAxVDAwOjAwOjAwKzAwOjAw'
                    'IiwidWluIjoiRklORV9VSU5fMDEiLCJtYXhfbG9hZGVkX2F0Ijoi'
                    'MjAyMi0wMS0wMVQwMDowMDowMCswMDowMCJ9'
                ),
            },
        },
    )

    assert (
        mock_api['fleet-reports-storage']['/internal/v1/file/upload']
        .next_call()['request']
        .get_data()
        .decode('cp1251')
        .replace('\r\n', '\n')
        == load('fines_bank_client2.txt')
    )
    assert pg_dump() == {
        **pg_initial,
        'load_operations': {
            **pg_initial['load_operations'],
            '1': (None, 'complete'),
        },
        'park_fines': {
            **pg_initial['park_fines'],
            ('FINE_UIN_02', 'CAR_ID_02', 'PARK-ID-01'): (
                'issued',
                dateutil.parser.parse('2021-12-31T00:00:00+00:00'),
                True,
                dateutil.parser.parse('2022-01-01T12:00:00+03:00'),
                dateutil.parser.parse('2022-01-01T03:00:00+03:00'),
                None,
            ),
        },
    }

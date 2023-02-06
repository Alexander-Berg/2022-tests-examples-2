import datetime
import decimal

import pytest


@pytest.mark.parametrize(
    'tariff_type, params, data, expected_status,'
    'expected_rule,'
    'expected_results',
    [
        # Wrong request
        (
            'support-taxi',
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-16',
                'calculation_rule_id': 'some_rule_id',
                'country': 'rus',
            },
            (
                'type,login,daytime_bo,night_bo,holidays_daytime_bo,'
                'holidays_night_bo,benefits\n'
                'intermediate,ivanov,2.5,5.0,qwe,1.5,\n'
                'final,petrov,3.0,3.0,3.0,3.0,3.0\n'
                'remove,smirnoff,,,,,\n'
            ),
            400,
            None,
            None,
        ),
        # Wrong request
        (
            'support-taxi',
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-16',
                'calculation_rule_id': 'some_rule_id',
                'country': 'rus',
            },
            (
                'type,login,daytime_bo,night_bo,holidays_daytime_bo,'
                'holidays_night_bo\n'
                'intermediate,ivanov,2.5,5.0,1.0,1.5\n'
                'final,petrov,3.0,3.0,3.0,3.0\n'
                'remove,smirnoff,,,,\n'
            ),
            400,
            None,
            None,
        ),
        # Payment not found
        (
            'support-taxi',
            {
                'start_date': '2020-02-01',
                'stop_date': '2020-02-16',
                'calculation_rule_id': 'some_rule_id',
                'country': 'rus',
            },
            (
                'type,login,daytime_bo,night_bo,holidays_daytime_bo,'
                'holidays_night_bo,benefits\n'
                'intermediate,ivanov,2.5,5.0,1.0,1.5,\n'
                'final,petrov,3.0,3.0,3.0,3.0,3.0\n'
                'remove,smirnoff,,,,,\n'
            ),
            409,
            None,
            None,
        ),
        # All OK
        (
            'support-taxi',
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-16',
                'calculation_rule_id': 'some_rule_id',
                'country': 'rus',
            },
            (
                'type,login,daytime_bo,night_bo,holidays_daytime_bo,'
                'holidays_night_bo,benefits\n'
                'intermediate,ivanov,2.5,5.0,1.0,1.5,\n'
                'final,petrov,3.0,3.0,3.0,3.0,3.0\n'
                'remove,smirnoff,,,,,\n'
            ),
            200,
            {
                'calculation_rule_id': 'some_rule_id',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'repeat': True,
                'countries': ['rus'],
                'logins': None,
                'enabled': True,
                'status': 'waiting_benefits',
                'description': 'Correction applied successfully',
            },
            [
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('10.0'),
                    'night_cost': decimal.Decimal('5.0'),
                    'holidays_daytime_cost': decimal.Decimal('8.0'),
                    'holidays_night_cost': decimal.Decimal('1.0'),
                    'calc_type': 'general',
                    'calc_subtype': 'chatterbox',
                },
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'petrov',
                    'daytime_cost': decimal.Decimal('15.0'),
                    'night_cost': decimal.Decimal('7.0'),
                    'holidays_daytime_cost': decimal.Decimal('10.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'calc_type': 'general',
                    'calc_subtype': 'chatterbox',
                },
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'smirnoff',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'calc_type': 'general',
                    'calc_subtype': 'chatterbox',
                },
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('2.5'),
                    'night_cost': decimal.Decimal('5.0'),
                    'holidays_daytime_cost': decimal.Decimal('1.0'),
                    'holidays_night_cost': decimal.Decimal('1.5'),
                    'calc_type': 'correction',
                    'calc_subtype': 'intermediate',
                },
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'petrov',
                    'daytime_cost': decimal.Decimal('3.0'),
                    'night_cost': decimal.Decimal('3.0'),
                    'holidays_daytime_cost': decimal.Decimal('3.0'),
                    'holidays_night_cost': decimal.Decimal('3.0'),
                    'calc_type': 'correction',
                    'calc_subtype': 'final',
                },
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'smirnoff',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'calc_type': 'correction',
                    'calc_subtype': 'remove',
                },
            ],
        ),
        # Multiple login, all OK
        (
            'support-taxi',
            {
                'start_date': '2020-01-01',
                'stop_date': '2020-01-16',
                'calculation_rule_id': 'some_rule_id',
                'country': 'rus',
            },
            (
                'type,login,daytime_bo,night_bo,holidays_daytime_bo,'
                'holidays_night_bo,benefits\n'
                'intermediate,ivanov,2.0,2.0,1.0,0.0,\n'
                'intermediate,ivanov,0.5,3.0,0.0,1.5,\n'
                'final,petrov,3.0,2.0,1.0,0.0,1.5\n'
                'final,petrov,0.0,1.0,2.0,3.0,1.5\n'
                'remove,smirnoff,,,,,\n'
            ),
            200,
            {
                'calculation_rule_id': 'some_rule_id',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'repeat': True,
                'countries': ['rus'],
                'logins': None,
                'enabled': True,
                'status': 'waiting_benefits',
                'description': 'Correction applied successfully',
            },
            [
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('10.0'),
                    'night_cost': decimal.Decimal('5.0'),
                    'holidays_daytime_cost': decimal.Decimal('8.0'),
                    'holidays_night_cost': decimal.Decimal('1.0'),
                    'calc_type': 'general',
                    'calc_subtype': 'chatterbox',
                },
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'petrov',
                    'daytime_cost': decimal.Decimal('15.0'),
                    'night_cost': decimal.Decimal('7.0'),
                    'holidays_daytime_cost': decimal.Decimal('10.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'calc_type': 'general',
                    'calc_subtype': 'chatterbox',
                },
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'smirnoff',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'calc_type': 'general',
                    'calc_subtype': 'chatterbox',
                },
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'ivanov',
                    'daytime_cost': decimal.Decimal('2.5'),
                    'night_cost': decimal.Decimal('5.0'),
                    'holidays_daytime_cost': decimal.Decimal('1.0'),
                    'holidays_night_cost': decimal.Decimal('1.5'),
                    'calc_type': 'correction',
                    'calc_subtype': 'intermediate',
                },
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'petrov',
                    'daytime_cost': decimal.Decimal('3.0'),
                    'night_cost': decimal.Decimal('3.0'),
                    'holidays_daytime_cost': decimal.Decimal('3.0'),
                    'holidays_night_cost': decimal.Decimal('3.0'),
                    'calc_type': 'correction',
                    'calc_subtype': 'final',
                },
                {
                    'calculation_rule_id': 'some_rule_id',
                    'start_date': datetime.date(2020, 1, 1),
                    'stop_date': datetime.date(2020, 1, 16),
                    'login': 'smirnoff',
                    'daytime_cost': decimal.Decimal('0.0'),
                    'night_cost': decimal.Decimal('0.0'),
                    'holidays_daytime_cost': decimal.Decimal('0.0'),
                    'holidays_night_cost': decimal.Decimal('0.0'),
                    'calc_type': 'correction',
                    'calc_subtype': 'remove',
                },
            ],
        ),
    ],
)
@pytest.mark.translations(
    piecework={
        'payment_ticket.summary': {
            'ru': 'Payment {country} per {start_date} - {stop_date}',
        },
        'payment_ticket.description': {
            'ru': 'Country: {country}\nPeriod: {start_date} - {stop_date}',
        },
    },
)
@pytest.mark.config(
    PIECEWORK_CALCULATION_PAYMENT_SETTINGS={
        'rus': {'ticket_locale': 'ru', 'destination': 'oebs'},
        'blr': {'ticket_locale': 'ru', 'destination': 'oebs', 'skip': True},
    },
)
async def test_import(
        web_context,
        web_app_client,
        mock_oebs_payments,
        tariff_type,
        params,
        data,
        expected_status,
        expected_rule,
        expected_results,
):
    response = await web_app_client.post(
        '/v1/corrections/{}/import'.format(tariff_type),
        params=params,
        data=_wrap_to_multipart(data),
        headers={'Content-Type': 'multipart/form-data; boundary=QWEASD'},
    )
    assert response.status == expected_status
    json_response = await response.json()
    if expected_status != 200:
        return
    assert json_response == {'approvals_id': 123}

    async with web_context.pg.slave_pool.acquire() as conn:
        pg_result = await conn.fetchrow(
            'SELECT '
            'calculation_rule_id, start_date, stop_date, repeat, countries, '
            'logins, enabled, status, description '
            'FROM piecework.calculation_rule WHERE calculation_rule_id = $1',
            params['calculation_rule_id'],
        )
        rule = dict(pg_result)
        assert rule == expected_rule

        pg_result = await conn.fetch(
            'SELECT '
            'calculation_rule_id, start_date, stop_date, login, '
            'daytime_cost, night_cost, holidays_daytime_cost, '
            'holidays_night_cost, calc_type, calc_subtype '
            'FROM piecework.calculation_result WHERE calculation_rule_id = $1 '
            'AND country = $2 '
            'ORDER BY calc_type, calc_subtype',
            params['calculation_rule_id'],
            params['country'],
        )
        pg_result = [dict(item) for item in pg_result]

        assert pg_result == expected_results

        pg_result = await conn.fetchrow(
            'SELECT COUNT(*) AS cnt '
            'FROM piecework.payment WHERE calculation_rule_id = $1 '
            'AND country = $2',
            params['calculation_rule_id'],
            params['country'],
        )
        assert pg_result['cnt'] == 0

        pg_result = await conn.fetch(
            'SELECT tariff_type, calculation_rule_id, country, start_date, '
            'stop_date, status, approvals_id '
            'FROM piecework.payment_draft WHERE calculation_rule_id = $1 '
            'AND country = $2',
            params['calculation_rule_id'],
            params['country'],
        )
        pg_result = [dict(item) for item in pg_result]
        assert pg_result == [
            {
                'tariff_type': 'support-taxi',
                'calculation_rule_id': 'some_rule_id',
                'country': 'rus',
                'start_date': datetime.date(2020, 1, 1),
                'stop_date': datetime.date(2020, 1, 16),
                'status': 'updating',
                'approvals_id': 123,
            },
        ]

        pg_result = await conn.fetchrow(
            'SELECT count(*) AS cnt '
            'FROM piecework.calculation_result WHERE calculation_rule_id = $1 '
            'AND calc_type = $2 AND country = $3',
            params['calculation_rule_id'],
            'correction',
            'blr',
        )
        assert pg_result['cnt'] > 0

        draft_status = await conn.fetchval(
            'SELECT status AS cnt '
            'FROM piecework.payment_draft WHERE calculation_rule_id = $1 '
            'AND country = $2',
            params['calculation_rule_id'],
            'blr',
        )
        assert draft_status == 'updating'


def _wrap_to_multipart(data):
    if isinstance(data, str):
        data = data.encode('utf8')
    multipart_data = b'--QWEASD\r\n'
    multipart_data += b'Content-disposition: attachment; '
    multipart_data += b'name=correction_file; filename=qwe.bin\r\n'
    multipart_data += b'Content-type: application/octet-stream\r\n\r\n'
    multipart_data += data
    multipart_data += b'\r\n--QWEASD--\r\n'
    return multipart_data

import pytest


SQL_INSERT_ORDER_TEMPLATE = (
    'INSERT INTO orders_0 '
    '(park_id, id, number, address_from, address_to, date_create, '
    'date_booking) '
    'VALUES (\'foo\', \'order{num}\', {num}, \'888\', \'999\', '
    '\'2018-02-21\', \'{date_booking}\')'
)


@pytest.mark.parametrize(
    'db_id,date_start,date_finish,expected_data',
    [
        (
            'foo',
            '2018-02-21',
            '2018-02-23',
            [
                {
                    'address_from': '888',
                    'address_to': '999',
                    'company_name': None,
                    'cost_total': 0.0,
                    'date_calling': None,
                    'date_create': '2018-02-21T00:00:00',
                    'date_drive': None,
                    'date_waiting': None,
                    'description': None,
                    'driver_signal': None,
                    'number': 1,
                    'payment': 0,
                    'phone1': None,
                    'phone2': None,
                    'phone3': None,
                    'rule_type_name': None,
                    'status': 0,
                    'tariff_name': None,
                },
            ],
        ),
    ],
)
@pytest.mark.pgsql(
    'orders',
    queries=[
        SQL_INSERT_ORDER_TEMPLATE.format(num=0, date_booking='2018-02-20'),
        SQL_INSERT_ORDER_TEMPLATE.format(num=1, date_booking='2018-02-21'),
        SQL_INSERT_ORDER_TEMPLATE.format(num=2, date_booking='2018-02-24'),
    ],
)
async def test_api(
        taximeter_reports_client,
        db_id,
        date_start,
        date_finish,
        expected_data,
):
    params = {
        'db_id': db_id,
        'date_start': date_start,
        'date_finish': date_finish,
    }
    response = await taximeter_reports_client.get('/orders', params=params)
    assert (await response.json()) == expected_data

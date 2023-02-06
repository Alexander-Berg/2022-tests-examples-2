# pylint: disable=redefined-outer-name, dangerous-default-value
# root conftest for service eats-picker-supply
import pytest


pytest_plugins = ['eats_picker_supply_plugins.pytest_plugins']


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_picker_supply'].dict_cursor()

    return create_cursor


@pytest.fixture()
def create_picker(get_cursor):
    def do_create_picker(
            picker_id='1',
            name='Пайкер Курьерович',
            phone_id='123456',
            places_ids=None,
            available_until='2020-09-20T23:00:00+03:00',
            priority=1,
            excluded_until=None,
            created_at='2020-09-20T11:54:00+03:00',
            updated_at='2020-09-20T11:54:12+03:00',
            synchronized_at='2020-09-20T11:54:06+03:00',
            requisite_type='TinkoffCard',
            requisite_value='000000000000',
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_picker_supply.pickers '
            '(picker_id, name, phone_id, places_ids, available_until, '
            'requisite_type, requisite_value, '
            'priority, excluded_until, created_at, updated_at, '
            'synchronized_at) '
            'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) '
            'RETURNING id',
            (
                picker_id,
                name,
                phone_id,
                places_ids or [],
                available_until,
                requisite_type,
                requisite_value,
                priority,
                excluded_until,
                created_at,
                updated_at,
                synchronized_at,
            ),
        )
        return cursor.fetchone()[0]

    return do_create_picker


@pytest.fixture()
def get_picker(get_cursor):
    def do_get_picker(picker_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_picker_supply.pickers WHERE id = %s',
            [picker_id],
        )
        return cursor.fetchone()

    return do_get_picker


@pytest.fixture(name='mock_eats_core_get_orders', autouse=True)
def eats_core_mockserver(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/eats-picker-orders/api/v1/orders')
    def eats_core(request):
        return mockserver.make_response(
            json=load_json('orders_expected_response.json'), status=200,
        )

    return eats_core

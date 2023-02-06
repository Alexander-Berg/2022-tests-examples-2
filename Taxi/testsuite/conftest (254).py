# pylint: disable=redefined-outer-name
import pytest

# root conftest for service eats-orders-tracking
pytest_plugins = ['eats_orders_tracking_plugins.pytest_plugins']


@pytest.fixture()
def get_cursor(pgsql):
    def create_cursor():
        return pgsql['eats_orders_tracking'].dict_cursor()

    return create_cursor


@pytest.fixture()
def create_order_info(get_cursor):
    def do_create_order_info(
            order_nr: str = '111111-222222',
            eater_id: str = '1',
            payload: str = '{"order_nr": "111111-222222",'
            '"status": "order.delivering",'
            '"status_detail": {'
            '"id": 3, '
            '"date": "2020-10-28T18:25:43.51"},'
            '"promise": 20,'
            '"location": {'
            '"latitude": 60.029139,'
            '"longitude": 30.144101},'
            '"is_asap": true,'
            '"delivery_type": "native",'
            '"shipping_type": "delivery",'
            '"place_id": "40",'
            '"courier_id": "100",'
            '"created_at": "2020-10-28T18:15:43.51",'
            '"updated_at": "2020-10-28T18:26:43.51",'
            '"service": "eats",'
            '"client_app": "taxi-app"}',
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_orders_tracking.orders '
            '(order_nr, eater_id, payload) '
            'VALUES (%s, %s, %s::jsonb) '
            'RETURNING order_nr',
            (order_nr, eater_id, payload),
        )
        return cursor.fetchone()[0]

    return do_create_order_info


@pytest.fixture()
def init_orders_info(create_order_info):
    create_order_info(
        order_nr='111111-222222',
        eater_id='1',
        payload='{"order_nr": "111111-222222",'
        '"status": "order.delivering",'
        '"status_detail": {'
        '"id": 3, '
        '"date": "2020-10-28T18:25:43.51"},'
        '"promise": 20,'
        '"location": {'
        '"latitude": 60.029139,'
        '"longitude": 30.144101},'
        '"is_asap": true,'
        '"delivery_type": "native",'
        '"shipping_type": "delivery",'
        '"place_id": "40",'
        '"courier_id": "100",'
        '"created_at": "2020-10-28T18:15:43.51",'
        '"updated_at": "2020-10-28T18:26:43.51",'
        '"service": "eats",'
        '"client_app": "taxi-app"}',
    )
    create_order_info(
        order_nr='111111-333333',
        eater_id='2',
        payload='{"order_nr": "111111-333333",'
        '"status": "order.delivering",'
        '"status_detail": {'
        '"id": 3, '
        '"date": "2020-10-28T18:25:43.51"},'
        '"promise": 20,'
        '"location": {'
        '"latitude": 60.029139,'
        '"longitude": 30.144101},'
        '"is_asap": true,'
        '"place_id": "41",'
        '"courier_id": "101",'
        '"delivery_type": "native",'
        '"shipping_type": "delivery",'
        '"place_id": "41",'
        '"created_at": "2020-10-28T18:15:43.51",'
        '"updated_at": "2020-10-28T18:26:43.51",'
        '"service": "eats",'
        '"client_app": "taxi-app"}',
    )
    create_order_info(
        order_nr='111111-444444',
        eater_id='3',
        payload='{"order_nr": "111111-444444",'
        '"status": "order.delivering",'
        '"status_detail": {'
        '"id": 3, '
        '"date": "2020-10-28T18:25:43.51"},'
        '"promise": 20,'
        '"location": {'
        '"latitude": 60.029139,'
        '"longitude": 30.144101},'
        '"is_asap": true,'
        '"delivery_type": "native",'
        '"shipping_type": "delivery",'
        '"place_id": "42",'
        '"courier_id": "102",'
        '"created_at": "2020-10-28T18:15:43.51",'
        '"updated_at": "2020-10-28T18:26:43.51",'
        '"service": "eats",'
        '"client_app": "taxi-app"}',
    )
    create_order_info(
        order_nr='111111-555555',
        eater_id='4',
        payload='{"order_nr": "111111-555555",'
        '"status": "order.delivering",'
        '"status_detail": {'
        '"id": 3, '
        '"date": "2020-10-28T18:25:43.51"},'
        '"promise": 20,'
        '"location": {'
        '"latitude": 60.029139,'
        '"longitude": 30.144101},'
        '"is_asap": true,'
        '"delivery_type": "native",'
        '"shipping_type": "delivery",'
        '"place_id": "43",'
        '"courier_id": "103",'
        '"created_at": "2020-10-28T18:15:43.51",'
        '"updated_at": "2020-10-28T18:26:43.51",'
        '"service": "eats",'
        '"client_app": "taxi-app"}',
    )
    create_order_info(
        order_nr='111111-666666',
        eater_id='5',
        payload='{"order_nr": "111111-666666",'
        '"status": "order.delivering",'
        '"status_detail": {'
        '"id": 3, '
        '"date": "2020-10-28T18:25:43.51"},'
        '"promise": 20,'
        '"location": {'
        '"latitude": 60.029139,'
        '"longitude": 30.144101},'
        '"is_asap": true,'
        '"delivery_type": "native",'
        '"shipping_type": "delivery",'
        '"place_id": "40",'
        '"courier_id": "100",'
        '"created_at": "2020-10-28T18:15:43.51",'
        '"updated_at": "2020-10-28T18:26:43.51",'
        '"service": "eats",'
        '"client_app": "taxi-app"}',
    )
    create_order_info(
        order_nr='111111-777777',
        eater_id='6',
        payload='{"order_nr": "111111-777777",'
        '"status": "order.delivering",'
        '"status_detail": {'
        '"id": 3, '
        '"date": "2020-10-28T18:25:43.51"},'
        '"promise": 20,'
        '"location": {'
        '"latitude": 60.029139,'
        '"longitude": 30.144101},'
        '"is_asap": true,'
        '"delivery_type": "native",'
        '"shipping_type": "delivery",'
        '"place_id": "41",'
        '"courier_id": "101",'
        '"created_at": "2020-10-28T18:15:43.51",'
        '"updated_at": "2020-10-28T18:26:43.51",'
        '"service": "eats",'
        '"client_app": "taxi-app"}',
    )
    create_order_info(
        order_nr='111111-888888',
        eater_id='7',
        payload='{"order_nr": "111111-888888",'
        '"status": "order.delivering",'
        '"status_detail": {'
        '"id": 3, '
        '"date": "2020-10-28T18:25:43.51"},'
        '"promise": 20,'
        '"location": {'
        '"latitude": 60.029139,'
        '"longitude": 30.144101},'
        '"is_asap": true,'
        '"delivery_type": "native",'
        '"shipping_type": "delivery",'
        '"place_id": "42",'
        '"courier_id": "102",'
        '"created_at": "2020-10-28T18:15:43.51",'
        '"updated_at": "2020-10-28T18:26:43.51",'
        '"service": "eats",'
        '"client_app": "taxi-app"}',
    )
    create_order_info(
        order_nr='111111-999999',
        eater_id='8',
        payload='{"order_nr": "111111-999999",'
        '"status": "order.delivering",'
        '"status_detail": {'
        '"id": 3, '
        '"date": "2020-10-28T18:25:43.51"},'
        '"promise": 20,'
        '"location": {'
        '"latitude": 60.029139,'
        '"longitude": 30.144101},'
        '"is_asap": true,'
        '"delivery_type": "native",'
        '"shipping_type": "delivery",'
        '"place_id": "43",'
        '"courier_id": "103",'
        '"created_at": "2020-10-28T18:15:43.51",'
        '"updated_at": "2020-10-28T18:26:43.51",'
        '"service": "eats",'
        '"client_app": "taxi-app"}',
    )


@pytest.fixture()
def create_place_info(get_cursor):
    def do_create_place_info(
            place_id: str = '40',
            payload: str = '{"id": "40",'
            '"name": "Вкусная Еда",'
            '"location": {'
            '"latitude": 59.999102,'
            '"longitude": 30.220117},'
            '"address": "Санкт-Петербург, ул. Оптиков, д. 30",'
            '"contacts": [{"type": "place",'
            '"phone": "+71234567890",'
            '"title": "title0"}]'
            '}',
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_orders_tracking.places '
            '(place_id, payload) '
            'VALUES (%s, %s::jsonb) '
            'RETURNING place_id',
            (place_id, payload),
        )
        return cursor.fetchone()[0]

    return do_create_place_info


@pytest.fixture()
def init_places_info(create_place_info):
    create_place_info(
        place_id='40',
        payload='{"id": "40",'
        '"name": "Вкусная Еда",'
        '"location": {'
        '"latitude": 59.999102,'
        '"longitude": 30.220117},'
        '"address": "Санкт-Петербург, ул. Оптиков, д. 30",'
        '"contacts": [{"type": "place",'
        '"phone": "+71234567890",'
        '"title": "title0"}]'
        '}',
    )
    create_place_info(
        place_id='41',
        payload='{"id": "41",'
        '"name": "Очень вкусная Еда",'
        '"location": {'
        '"latitude": 59.999102,'
        '"longitude": 30.220117},'
        '"address": "Санкт-Петербург, ул. Оптиков, д. 30",'
        '"contacts": [{"type": "place",'
        '"phone": "+71234567892",'
        '"title": "title2"}]'
        '}',
    )
    create_place_info(
        place_id='42',
        payload='{"id": "42",'
        '"name": "Так себе Еда",'
        '"location": {'
        '"latitude": 59.999102,'
        '"longitude": 30.220117},'
        '"address": "Санкт-Петербург, ул. Оптиков, д. 30",'
        '"contacts": [{"type": "place",'
        '"phone": "+71234567894",'
        '"title": "title4"}]'
        '}',
    )
    create_place_info(
        place_id='43',
        payload='{"id": "43",'
        '"name": "Никудышная Еда",'
        '"location": {'
        '"latitude": 59.999102,'
        '"longitude": 30.220117},'
        '"address": "Санкт-Петербург, ул. Оптиков, д. 30",'
        '"contacts": [{"type": "place",'
        '"phone": "+71234567896",'
        '"title": "title6"}]'
        '}',
    )


@pytest.fixture()
def create_courier_info(get_cursor):
    def do_create_courier_info(
            order_nr: str = '000000-000000',
            payload: str = '{"id": "100",'
            '"name": "Курьер Пешкодралович",'
            '"is_hard_of_hearing": false,'
            '"contacts":[{"type": "courier",'
            '"phone": "+79876543210",'
            '"title": "courier0"}]}',
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_orders_tracking.couriers '
            '(order_nr, payload) '
            'VALUES (%s, %s::jsonb) '
            'RETURNING order_nr',
            (order_nr, payload),
        )
        return cursor.fetchone()[0]

    return do_create_courier_info


@pytest.fixture()
def init_couriers_info(create_courier_info):
    create_courier_info(
        order_nr='000000-000000',
        payload='{"id": "100",'
        '"name": "Курьер Пешкодралович",'
        '"is_hard_of_hearing": false,'
        '"contacts":[{"type": "courier",'
        '"phone": "+79876543210",'
        '"title": "courier0"}]}',
    )
    create_courier_info(
        order_nr='000000-111111',
        payload='{"id": "101",'
        '"name": "Курьер Велосипедович",'
        '"is_hard_of_hearing": false,'
        '"contacts":[{"type": "courier",'
        '"phone": "+79876543211",'
        '"title": "courier1"}]}',
    )
    create_courier_info(
        order_nr='000000-222222',
        payload='{"id": "102",'
        '"name": "Курьер Самокатович",'
        '"is_hard_of_hearing": false,'
        '"contacts":[{"type": "courier",'
        '"phone": "+79876543212",'
        '"title": "courier2"}]}',
    )
    create_courier_info(
        order_nr='000000-333333',
        payload='{"id": "103",'
        '"name": "Курьер Автомобилевич",'
        '"is_hard_of_hearing": false,'
        '"contacts":[{"type": "courier",'
        '"phone": "+79876543213",'
        '"title": "courier3"}],'
        '"car_number": "a000aa178"}',
    )


@pytest.fixture()
def create_display_type(get_cursor):
    def do_create_display_type(
            display_type_code: str = 'display1',
            title: str = 'title display 1',
            description: str = 'description display 1',
            buttons: str = '[]',
            icons: str = '[]',
    ):
        cursor = get_cursor()
        cursor.execute(
            'INSERT INTO eats_orders_tracking.display_types '
            '(display_type_code, title, description, buttons, icons) '
            'VALUES (%s, %s, %s, %s::jsonb, %s::jsonb) '
            'RETURNING display_type_code',
            (display_type_code, title, description, buttons, icons),
        )
        return cursor.fetchone()[0]

    return do_create_display_type


@pytest.fixture()
def init_display_types(create_display_type):
    create_display_type(
        display_type_code='display1',
        title='title display 1',
        description='title display 1',
        buttons='['
        '{"type": "type1", "title": "title1", "payload": {}, "actions": {}},'
        '{"type": "type2", "title": "title2", "payload": {}, "actions": {}}'
        ']',
        icons='['
        '{"status": "status1",'
        '"uri": "https://example.com/icon1",'
        '"payload": {}},'
        '{"status": "status2",'
        '"uri": "https://example.com/icon2",'
        '"payload": {}}'
        ']',
    )
    create_display_type(
        display_type_code='display2',
        title='title display 2',
        description='title display 1',
        buttons='['
        '{"type": "type1", "title": "title1", "payload": {}, "actions": {}},'
        '{"type": "type2", "title": "title2", "payload": {}, "actions": {}}'
        ']',
        icons='['
        '{"status": "status1",'
        '"uri": "https://example.com/icon1",'
        '"payload": {}},'
        '{"status": "status2",'
        '"uri": "https://example.com/icon2",'
        '"payload": {}}'
        ']',
    )
    create_display_type(
        display_type_code='display3',
        title='title display 3',
        description='title display 1',
        buttons='['
        '{"type": "type1", "title": "title1", "payload": {}, "actions": {}},'
        '{"type": "type2", "title": "title2", "payload": {}, "actions": {}}'
        ']',
        icons='['
        '{"status": "status1",'
        '"uri": "https://example.com/icon1",'
        '"payload": {}},'
        '{"status": "status2",'
        '"uri": "https://example.com/icon2",'
        '"payload": {}}'
        ']',
    )
    create_display_type(
        display_type_code='display4',
        title='title display 4',
        description='title display 1',
        buttons='['
        '{"type": "type1", "title": "title1", "payload": {}, "actions": {}},'
        '{"type": "type2", "title": "title2", "payload": {}, "actions": {}}'
        ']',
        icons='['
        '{"status": "status1",'
        '"uri": "https://example.com/icon1",'
        '"payload": {}},'
        '{"status": "status2",'
        '"uri": "https://example.com/icon2",'
        '"payload": {}}'
        ']',
    )


@pytest.fixture()
def get_order_info(get_cursor):
    def do_get_order_info(order_nr):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_orders_tracking.orders  WHERE order_nr = %s',
            [order_nr],
        )
        return cursor.fetchone()

    return do_get_order_info


@pytest.fixture()
def get_place_info(get_cursor):
    def do_get_place_info(place_id):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_orders_tracking.places  WHERE place_id = %s',
            [place_id],
        )
        return cursor.fetchone()

    return do_get_place_info


@pytest.fixture()
def get_display_type(get_cursor):
    def do_get_display_type(display_type_code):
        cursor = get_cursor()
        cursor.execute(
            'SELECT * FROM eats_orders_tracking.display_types'
            ' WHERE display_type_code = %s',
            [display_type_code],
        )
        return cursor.fetchone()

    return do_get_display_type

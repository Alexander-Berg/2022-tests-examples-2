import dateutil.parser
import pytest

from tests_plugins import utils

# pylint: disable=invalid-name, too-many-arguments
@pytest.mark.parametrize(
    'time,newer_than,timezone,driver_uuid,'
    'events_processed_code,events_processed_response,'
    'bulk_retrieve_code,bulk_retrieve_orders,'
    'expected_code,expected_response',
    [
        (
            '2020-03-17T14:45:00+0300',
            '2020-03-10T14:45:00.000000Z',
            'Europe/Moscow',
            'driver_uuid1',
            200,
            'events_processed_response_success.json',
            200,
            'bulk_retrieve_orders_success.json',
            200,
            'expected_response_success.json',
        ),
        (
            '2020-03-17T14:45:00+0300',
            '2020-03-10T14:45:00.000000Z',
            'Europe/Moscow',
            'driver_uuid1',
            200,
            'events_processed_response_empty.json',
            200,
            'bulk_retrieve_orders_empty.json',
            200,
            'expected_response_no_orders.json',
        ),
        (
            '2020-03-17T14:45:00+0300',
            '2020-03-10T14:45:00.000000Z',
            'Europe/Moscow',
            'missing_driver_uuid',
            200,
            'events_processed_response_success.json',
            200,
            'bulk_retrieve_orders_success.json',
            404,
            'expected_response_404.json',
        ),
        (
            '2020-03-17T14:45:00+0300',
            '2020-03-10T14:45:00.000000Z',
            'Europe/Moscow',
            'driver_uuid1',
            500,
            'events_processed_response_error.json',
            200,
            'bulk_retrieve_orders_empty.json',
            200,
            'expected_response_history_unavailable.json',
        ),
        (
            '2020-03-17T14:45:00+0300',
            '2020-03-10T14:45:00.000000Z',
            'Europe/Moscow',
            'driver_uuid1',
            400,
            'events_processed_response_error.json',
            200,
            'bulk_retrieve_orders_empty.json',
            200,
            'expected_response_history_unavailable.json',
        ),
        (
            '2020-03-17T14:45:00+0300',
            '2020-03-10T14:45:00.000000Z',
            'Europe/Moscow',
            'driver_uuid1',
            200,
            'events_processed_response_success.json',
            500,
            'bulk_retrieve_orders_empty.json',
            200,
            'expected_response_history_unavailable.json',
        ),
        (
            '2020-03-17T14:45:00+0300',
            '2020-03-10T14:45:00.000000Z',
            'Europe/Moscow',
            'driver_uuid1',
            200,
            'events_processed_response_success.json',
            500,
            'bulk_retrieve_orders_empty.json',
            200,
            'expected_response_history_unavailable.json',
        ),
    ],
)
@pytest.mark.config(
    TARIFF_CLASSES_MAPPING={
        'business2': {'classes': ['business']},
        'cargocorp': {'classes': ['cargo']},
        'mkk_antifraud': {'classes': ['econom']},
        'special': {'classes': ['business']},
        'uberblack': {'classes': ['vip']},
        'uberkids': {
            'classes': ['child_tariff'],
            'requirements': [{'childchair': 3}],
        },
        'uberlux': {'classes': ['ultimate']},
        'ubernight': {'classes': ['express']},
        'uberselect': {'classes': ['business']},
        'uberselectplus': {'classes': ['comfortplus']},
        'uberstart': {'classes': ['start']},
        'ubervan': {'classes': ['minivan']},
        'uberx': {'classes': ['econom']},
        'vezetbusiness': {'classes': ['business']},
        'vezeteconom': {'classes': ['econom']},
    },
)
async def test_driver_loyalty_balance_history(
        taxi_loyalty,
        driver_metrics_storage,
        driver_orders,
        unique_drivers,
        load_json,
        time,
        newer_than,
        timezone,
        driver_uuid,
        events_processed_code,
        events_processed_response,
        bulk_retrieve_code,
        bulk_retrieve_orders,
        expected_code,
        expected_response,
        mocked_time,
):
    unique_drivers.set_unique_driver(
        'driver_db_id1', 'driver_uuid1', 'unique_driver_id1',
    )

    driver_metrics_storage.set_events_processed_response(
        load_json('events_processed_response/' + events_processed_response),
        events_processed_code,
    )

    driver_orders.set_bulk_retrieve_response_code(bulk_retrieve_code)
    json = load_json('bulk_retrieve_orders/' + bulk_retrieve_orders)
    for order in json['orders']:
        driver_orders.add_bulk_retrieve_order(order['id'], order['order'])

    mocked_time.set(utils.to_utc(dateutil.parser.parse(time)))
    await taxi_loyalty.invalidate_caches()

    response = await taxi_loyalty.get(
        'driver/v1/loyalty/v1/balance-history',
        params={'newer_than': newer_than, 'timezone': timezone},
        headers={
            'Accept-Language': 'ru',
            'X-YaTaxi-Park-Id': 'driver_db_id1',
            'X-YaTaxi-Driver-Profile-Id': driver_uuid,
            'X-Request-Application': 'taximeter',
            'X-Request-Application-Version': '9.07 (1234)',
            'X-Request-Version-Type': '',
            'X-Request-Platform': 'android',
        },
    )
    # Входным данным (passenger_category) comfortplus
    # соответствует танкерный ключ, мок которого отличается от реального.
    # Ему соответствует:
    #       - в моках кэша:     car_category_comfort_plus
    #                           car_category_comfortplus
    #       - в реальности: car_category_comport_plus
    # Мок кэша расположен в библиотеке:
    # driver-categories-cache/testsuite/static/default/all_categories.json
    # Поэтому в НАШИХ моках локалайзера  (driver_localizer_.Get(tanker_key))
    # будем обрабатывать как замоканные, так и реальные ключи:
    #       car_category_comfort_plus -->  Комфорт+
    #       car_category_comfortplus  -->  Комфорт+
    #       car_category_comport_plus -->  Комфорт+
    # (см default/localizations/taximeter_backend_driver_messages.json)
    assert response.status_code == expected_code
    assert response.json() == load_json(
        'balance_history_response/' + expected_response,
    )

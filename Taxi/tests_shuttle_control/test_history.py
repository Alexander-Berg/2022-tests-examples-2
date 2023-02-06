# pylint: disable=import-error, import-only-modules
import pytest

from tests_shuttle_control.utils import select_named

STATE_HISTORY = ['items/state_0.json', 'items/state_1.json']
ARCHIVE_HISTORY = [
    'items/archive_0.json',
    'items/archive_1.json',
    'items/archive_2.json',
    'items/archive_3.json',
]
YAMAPS_ADDRESS = [
    {
        'business': {
            'address': {
                'formatted_address': 'Russia, Moscow',
                'country': 'Russia',
                'locality': 'Moscow',
            },
            'name': 'One-door community',
            'closed': 'UNKNOWN',
            'class': 'restaurant',
            'id': '1088700971',
        },
        'uri': 'ymapsbm1://URI_0_0',
        'name': 'short_order_point_text_translated',
        'description': 'Moscow, Russia',
        'geometry': [37.0, 55.0],
    },
]


@pytest.fixture(autouse=True)
def mock_driver_profiles(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/driver-profiles/v1/driver/profiles/retrieve')
    def profile_retrieve_handler(request):
        response = {'profiles': []}
        for profile_id in set(request.json['id_in_set']):
            _, uuid = profile_id.split('_')
            response['profiles'].append(
                {
                    'revision': '0_1546300750_1',
                    'park_driver_profile_id': profile_id,
                    'data': {
                        'full_name': {
                            'first_name': 'Ivan',
                            'middle_name': 'Ivanovich',
                            'second_name': 'Ivanov',
                        },
                        'car_id': 'carid42',
                        'phone_pd_ids': [{'pd_id': 'phone_pd_id1'}],
                        'uuid': uuid,
                        'license': {
                            'pd_id': 'df06ebff06954bfe91da47f097952a7d',
                        },
                    },
                },
            )
        return response


@pytest.fixture(autouse=True)
def mock_vehicles_retrieve(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/fleet-vehicles/v1/vehicles/retrieve')
    def vehicle_retrieve_handler(request):
        response_json = {'vehicles': []}
        for vehicle_id in request.json['id_in_set']:
            park_id, car_id = vehicle_id.split('_')
            response_json['vehicles'].append(
                {
                    'data': {
                        'park_id': park_id,
                        'car_id': car_id,
                        'number': 'Е226ОО197',
                        'brand': 'Mazda',
                        'model': '5',
                        'color': 'red',
                    },
                    'park_id_car_id': vehicle_id,
                },
            )
        return response_json


@pytest.fixture(autouse=True)
def mock_fleet_parks(mockserver, load_json):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/fleet-parks/v1/parks/list')
    def parks_list(request):
        response_json = {'parks': []}
        for park_id in request.json['query']['park']['ids']:
            park_data = load_json('parks_list_item.json')
            park_data['id'] = park_id
            park_data['provider_config']['clid'] = 'clid' + park_id
            response_json['parks'].append(park_data)
        return response_json


@pytest.fixture(autouse=True)
def mock_park_replica(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/parks-replica/v1/parks/retrieve')
    def parks_retrieve(request):
        response_json = {'parks': []}
        for park_id in request.json['id_in_set']:
            response_json['parks'].append(
                {
                    'park_id': park_id,
                    'data': {
                        'email_pd_id': '9497e2d3462f482f859e0ed5cf0a83ba',
                        'long_name': (
                            'Индивидуальный предприниматель'
                            ' Юдаков Максим Викторович'
                        ),
                        'name': 'Село',
                        'phone_pd_id': '05b7fdfdbac14b28a0c8f8545c887512',
                        'legal_address': 'Улица Пушкина, дом Копушкина',
                        'ogrn': '222200003333',
                    },
                },
            )
        return response_json


@pytest.fixture(autouse=True)
def mock_cars_catalog(mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/cars-catalog/api/v1/cars/get_color')
    def get_color(request):
        return {'normalized_color': 'красный', 'color_code': 'FF0000'}


@pytest.fixture(autouse=True)
def yamaps_wrapper(yamaps):
    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        for addr in YAMAPS_ADDRESS:
            return [addr]
        return []


async def process_history_item(order, full_address: bool):
    new_order = {}
    simple_copy = [
        'created_at',
        'order_id',
        'image_tag',
        'is_active',
        'payment',
        'status',
        'tariff_class',
        'vehicle',
        'driver',
        'quality_question_link',
    ]
    for idx in simple_copy:
        if idx in order:
            new_order[idx] = order[idx]
    new_order['route'] = {}
    if full_address:
        new_order['route']['source'] = 'short_order_point_text_translated'
        new_order['route']['destination'] = 'short_order_point_text_translated'
    else:
        new_order['route']['source'] = order['route']['source']['short_text']
        new_order['route']['destination'] = order['route']['destinations'][0][
            'short_text'
        ]
    return new_order


@pytest.mark.now('2020-06-20T12:29:58+0000')
@pytest.mark.experiments3(filename='exp3_shuttle_quality_question.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'older_than, results, expected_responses',
    [
        (None, 10, STATE_HISTORY + ARCHIVE_HISTORY),
        (None, 1, [STATE_HISTORY[0]]),
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730775', 100, ARCHIVE_HISTORY),
        (
            '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
            100,
            [STATE_HISTORY[1]] + ARCHIVE_HISTORY,
        ),
        ('89fe0a27-9a5d-4c73-bfee-f099d7f8488c', 100, ARCHIVE_HISTORY[1:]),
    ],
)
@pytest.mark.parametrize(
    'full_address',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=True),
            id='full_address_info_enabled',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=False),
            id='full_address_info_disabled',
        ),
    ],
)
async def test_history_list(
        taxi_shuttle_control,
        load_json,
        older_than,
        results,
        full_address,
        expected_responses,
):
    request = {'range': {}}
    if older_than is not None:
        request['range']['older_than'] = {
            'order_id': older_than,
            'created_at': 0,
        }
    request['range']['results'] = results
    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/booking/history/list',
        headers={'X-Yandex-UID': '0123456789'},
        json=request,
    )
    expected_responses = [
        await process_history_item(load_json(path), full_address)
        for path in expected_responses
    ]
    assert response.json()['orders'] == expected_responses


@pytest.mark.now('2020-06-20T12:29:58+0000')
@pytest.mark.experiments3(filename='exp3_shuttle_quality_question.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'order_id, expected_result',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730776', 'items/state_0.json'),
        ('ee3d7564-8340-45dc-a25d-c3ee9deba2d6', 'items/archive_2.json'),
    ],
)
@pytest.mark.parametrize(
    'full_address',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=True),
            id='full_address_info_enabled',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(SHUTTLE_CONTROL_FULL_ADDRESS_INFO=False),
            id='full_address_info_disabled',
        ),
    ],
)
async def test_history_item(
        taxi_shuttle_control,
        load_json,
        order_id,
        full_address,
        expected_result,
):
    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/booking/history/item',
        headers={'X-Yandex-UID': '0123456789'},
        json={'order_id': order_id},
    )
    expected_result = load_json(expected_result)
    if full_address:
        expected_result['route']['source'][
            'short_text'
        ] = 'short_order_point_text_translated'
        expected_result['route']['destinations'][0][
            'short_text'
        ] = 'short_order_point_text_translated'
    assert response.json()['order'] == expected_result


@pytest.mark.now('2020-06-20T12:29:58+0000')
@pytest.mark.experiments3(filename='exp3_shuttle_quality_question.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'order_id, expected_result',
    [
        ('2fef68c9-25d0-4174-9dd0-bdd1b3730776', 'items/state_0.json'),
        ('ee3d7564-8340-45dc-a25d-c3ee9deba2d6', 'items/archive_2.json'),
    ],
)
async def test_history_item_missing(
        taxi_shuttle_control, order_id, expected_result,
):
    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/booking/history/item',
        headers={'X-Yandex-UID': '0123456789'},
        json={'order_id': '2fef68c9-25d0-4174-9dd0-000000000000'},
    )
    assert response.status_code == 404


@pytest.mark.now('2020-06-20T12:29:58+0000')
@pytest.mark.experiments3(filename='exp3_shuttle_quality_question.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'order_id',
    [
        '2fef68c9-25d0-4174-9dd0-bdd1b3730776',
        'ee3d7564-8340-45dc-a25d-c3ee9deba2d6',
        '00000000-0000-0000-0000-000000000000',
    ],
)
async def test_history_remove(taxi_shuttle_control, order_id, pgsql):
    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/booking/history/remove',
        headers={'X-Yandex-UID': '0123456789'},
        json={'order_id': order_id},
    )

    assert response.status_code == 200
    rows = select_named(
        f'SELECT booking_id FROM state.passengers '
        f'WHERE booking_id = \'{order_id}\'',
        pgsql['shuttle_control'],
    )
    assert not rows

    rows = select_named(
        f'SELECT booking_id FROM archive.bookings '
        f'WHERE booking_id = \'{order_id}\'',
        pgsql['shuttle_control'],
    )
    assert not rows

    order_points_info_rows = select_named(
        f'SELECT booking_id FROM state.order_point_text_info '
        f'WHERE booking_id = \'{order_id}\'',
        pgsql['shuttle_control'],
    )
    assert not order_points_info_rows


@pytest.mark.now('2020-06-20T12:29:58+0000')
@pytest.mark.experiments3(filename='exp3_shuttle_quality_question.json')
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_history_remove_active_order(taxi_shuttle_control, pgsql):
    response = await taxi_shuttle_control.post(
        '/internal/shuttle-control/v1/booking/history/remove',
        headers={'X-Yandex-UID': '0123456789'},
        json={'order_id': '2fef68c9-25d0-4174-9dd0-bdd1b3730775'},
    )

    assert response.status_code == 400
    rows = select_named(
        f'SELECT booking_id FROM state.passengers '
        f'WHERE booking_id = \'2fef68c9-25d0-4174-9dd0-bdd1b3730775\'',
        pgsql['shuttle_control'],
    )
    assert rows

    order_points_info_rows = select_named(
        f'SELECT booking_id FROM state.order_point_text_info '
        f'WHERE booking_id = \'2fef68c9-25d0-4174-9dd0-bdd1b3730775\'',
        pgsql['shuttle_control'],
    )
    assert len(order_points_info_rows) == 2

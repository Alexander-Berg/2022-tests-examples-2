# pylint: disable=import-only-modules
import pytest

from tests_shuttle_control.utils import select_named


def _exclude_none(input_map):
    return {
        key: value for key, value in input_map.items() if value is not None
    }


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'test route': {
            'driver': 'shuttle_control.routes.route.name_for_driver',
            'passenger': 'shuttle_control.routes.route.name_for_passenger',
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'shuttle_control.stops.stop0': {'ru': 'Остановка 0, 0'},
        'shuttle_control.stops.stop010': {'ru': 'Остановка 0, 10'},
        'shuttle_control.stops.stop10': {'ru': 'Остановка 10, 10'},
        'shuttle_control.stops.stop22': {'ru': 'Остановка 22, 12'},
        'shuttle_control.stops.stop40': {'ru': 'Остановка 40, 40'},
        'shuttle_control.stops.stop42': {'ru': 'Остановка 42, 42'},
        'shuttle_control.routes.route.name_for_driver': {
            'ru': 'Водительский маршрут',
        },
        'shuttle_control.routes.route.name_for_passenger': {
            'ru': 'Пассажирский маршрут',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'is_dynamic, response_json_file',
    [
        (False, 'admin_static_routes_list.json'),
        (True, 'admin_dynamic_routes_list.json'),
    ],
)
async def test_add_remove(
        taxi_shuttle_control, is_dynamic, response_json_file, pgsql, load_json,
):
    # point, stop_name, is_required
    route_data = [
        ([0, 0], 'stop0' if is_dynamic else None, True, False),
        ([0, 10], 'stop010' if is_dynamic else None, True, False),
        ([10, 10], 'stop10', True, is_dynamic),
        ([22, 12], 'stop22' if is_dynamic else None, not is_dynamic, False),
        ([40, 40], 'stop40' if is_dynamic else None, None, False),
        ([42, 42], 'stop42', None, False),
    ]

    route = [
        _exclude_none(
            {
                'point': point,
                'is_stop': stop_name is not None,
                'name': stop_name,
                'is_required': is_required,
                'is_terminal': is_terminal,
            },
        )
        for point, stop_name, is_required, is_terminal in route_data
    ]
    response = await taxi_shuttle_control.put(
        '/admin/shuttle-control/v1/routes/item',
        json={
            'name': 'test route',
            'is_cyclic': False,
            'is_dynamic': is_dynamic,
            'route': route,
        },
    )

    assert response.status_code == 200
    assert response.json() == {'route_id': 'Pmp80rQ23L4wZYxd'}

    response = await taxi_shuttle_control.get(
        '/admin/shuttle-control/v1/routes/list',
    )
    assert response.status_code == 200
    assert response.json() == load_json(response_json_file)

    rows = select_named(
        'SELECT route_id, name, is_deleted FROM config.routes',
        pgsql['shuttle_control'],
    )
    assert len(rows) == 2
    row = rows[0] if rows[0]['route_id'] == 2 else rows[1]
    assert row['name'] == 'test route'
    assert not row['is_deleted']

    rows = select_named(
        'SELECT crp.point_id, cp.position, crp.point_order,'
        'cs.stop_id, cs.name, cs.is_terminal '
        'FROM config.route_points crp '
        'INNER JOIN config.points cp '
        'ON cp.point_id = crp.point_id '
        'LEFT JOIN config.stops cs '
        'ON cs.point_id = cp.point_id '
        'WHERE crp.route_id = 2 '
        'ORDER BY crp.point_id ASC',
        pgsql['shuttle_control'],
    )
    assert len(rows) == 6

    point_ids = iter(range(2, 2 + 6))
    point_orders = iter(range(1, 1 + 6))
    stop_ids = iter(range(2, 2 + 6))
    expected_rows = []
    for point, stop_name, is_required, is_terminal in route_data:
        expected_rows.append(
            {
                'is_terminal': is_terminal if stop_name else None,
                'point_id': next(point_ids),
                'position': f'({point[0]},{point[1]})',
                'point_order': (
                    next(point_orders) if is_required is not False else None
                ),
                'stop_id': next(stop_ids) if stop_name else None,
                'name': stop_name,
            },
        )
    assert rows == expected_rows

    response = await taxi_shuttle_control.delete(
        '/admin/shuttle-control/v1/routes/item',
        params={'route_id': 'Pmp80rQ23L4wZYxd'},
    )
    assert response.status_code == 200

    rows = select_named(
        'SELECT route_id, name, is_deleted FROM config.routes',
        pgsql['shuttle_control'],
    )
    assert len(rows) == 2
    row = rows[0] if rows[0]['route_id'] == 2 else rows[1]
    assert row['name'] == 'test route'
    assert row['is_deleted']


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'test route': {
            'driver': 'shuttle_control.routes.route.name_for_driver',
            'passenger': 'shuttle_control.routes.route.name_for_passenger',
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'shuttle_control.stops.stop10': {'ru': 'Остановка 10, 10'},
        'shuttle_control.stops.stop22': {'ru': 'Остановка 22, 12'},
        'shuttle_control.stops.stop42': {'ru': 'Остановка 42, 42'},
        'shuttle_control.routes.route.name_for_driver': {
            'ru': 'Водительский маршрут',
        },
        'shuttle_control.routes.route.name_for_passenger': {
            'ru': 'Пассажирский маршрут',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_add_override(taxi_shuttle_control, mockserver, pgsql):
    response = await taxi_shuttle_control.put(
        '/admin/shuttle-control/v1/routes/item',
        json={
            'name': 'test route',
            'is_cyclic': False,
            'route': [
                {'point': [0, 0], 'is_stop': False},
                {'point': [0, 10], 'is_stop': False},
                {
                    'point': [10, 10],
                    'is_stop': True,
                    'name': 'stop10',
                    'ya_transport_stop_id': 'stop_point_10',
                },
                {
                    'point': [22, 12],
                    'is_stop': True,
                    'name': 'stop22',
                    'ya_transport_stop_id': 'stop_point_22',
                },
                {'point': [40, 40], 'is_stop': False},
                {'point': [42, 42], 'is_stop': True, 'name': 'stop42'},
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'route_id': 'Pmp80rQ23L4wZYxd'}

    rows = select_named(
        'SELECT route_id, name, is_deleted, version FROM config.routes',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'route_id': 1,
            'name': 'main_route',
            'is_deleted': False,
            'version': 1,
        },
        {
            'route_id': 2,
            'name': 'test route',
            'is_deleted': False,
            'version': 1,
        },
    ]

    rows = select_named(
        'SELECT crp.point_id, cp.position, crp.point_order,'
        'cs.stop_id, cs.name '
        'FROM config.route_points crp '
        'INNER JOIN config.points cp '
        'ON cp.point_id = crp.point_id '
        'LEFT JOIN config.stops cs '
        'ON cs.point_id = cp.point_id '
        'WHERE crp.route_id = 2 '
        'ORDER BY crp.point_order ASC',
        pgsql['shuttle_control'],
    )
    assert len(rows) == 6
    assert rows == [
        {
            'point_id': 2,
            'position': '(0,0)',
            'point_order': 1,
            'stop_id': None,
            'name': None,
        },
        {
            'point_id': 3,
            'position': '(0,10)',
            'point_order': 2,
            'stop_id': None,
            'name': None,
        },
        {
            'point_id': 4,
            'position': '(10,10)',
            'point_order': 3,
            'stop_id': 2,
            'name': 'stop10',
        },
        {
            'point_id': 5,
            'position': '(22,12)',
            'point_order': 4,
            'stop_id': 3,
            'name': 'stop22',
        },
        {
            'point_id': 6,
            'position': '(40,40)',
            'point_order': 5,
            'stop_id': None,
            'name': None,
        },
        {
            'point_id': 7,
            'position': '(42,42)',
            'point_order': 6,
            'stop_id': 4,
            'name': 'stop42',
        },
    ]

    response = await taxi_shuttle_control.put(
        '/admin/shuttle-control/v1/routes/item',
        json={
            'name': 'test route',
            'is_cyclic': False,
            'is_dynamic': False,
            'route': [
                {'point': [0, 0], 'is_stop': False},
                {
                    'point': [22, 12],
                    'is_stop': True,
                    'name': 'stop22',
                    'ya_transport_stop_id': 'stop_point_22',
                },
                {'point': [0, 10], 'is_stop': False},
                {'point': [42, 42], 'is_stop': True, 'name': 'stop42'},
                {
                    'point': [10, 10],
                    'is_stop': True,
                    'name': 'stop10',
                    'ya_transport_stop_id': 'stop_point_10',
                },
            ],
        },
    )

    assert response.status_code == 200
    assert response.json() == {'route_id': '80vm7DQm7Ml24ZdO'}

    rows = select_named(
        'SELECT route_id, name, is_deleted, version FROM config.routes',
        pgsql['shuttle_control'],
    )

    assert rows == [
        {
            'route_id': 1,
            'name': 'main_route',
            'is_deleted': False,
            'version': 1,
        },
        {
            'route_id': 2,
            'name': 'test route',
            'is_deleted': True,
            'version': 1,
        },
        {
            'route_id': 3,
            'name': 'test route',
            'is_deleted': False,
            'version': 2,
        },
    ]

    rows = select_named(
        'SELECT crp.point_id, cp.position, crp.point_order,'
        'cs.stop_id, cs.name '
        'FROM config.route_points crp '
        'INNER JOIN config.points cp '
        'ON cp.point_id = crp.point_id '
        'LEFT JOIN config.stops cs '
        'ON cs.point_id = cp.point_id '
        'WHERE crp.route_id = 3 '
        'ORDER BY crp.point_order ASC',
        pgsql['shuttle_control'],
    )
    assert len(rows) == 5
    assert rows == [
        {
            'point_id': 8,
            'position': '(0,0)',
            'point_order': 1,
            'stop_id': None,
            'name': None,
        },
        {
            'point_id': 5,
            'position': '(22,12)',
            'point_order': 2,
            'stop_id': 3,
            'name': 'stop22',
        },
        {
            'point_id': 10,
            'position': '(0,10)',
            'point_order': 3,
            'stop_id': None,
            'name': None,
        },
        {
            'point_id': 11,
            'position': '(42,42)',
            'point_order': 4,
            'stop_id': 6,
            'name': 'stop42',
        },
        {
            'point_id': 4,
            'position': '(10,10)',
            'point_order': 5,
            'stop_id': 2,
            'name': 'stop10',
        },
    ]


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'test route': {
            'driver': 'shuttle_control.routes.route.name_for_driver',
            'passenger': 'shuttle_control.routes.route.name_for_passenger',
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'shuttle_control.stops.stop10': {'ru': 'Остановка 10, 10'},
        'shuttle_control.stops.stop22': {'ru': 'Остановка 22, 12'},
        'shuttle_control.stops.stop42': {'ru': 'Остановка 42, 42'},
        'shuttle_control.routes.route.name_for_driver': {
            'ru': 'Водительский маршрут',
        },
        'shuttle_control.routes.route.name_for_passenger': {
            'ru': 'Пассажирский маршрут',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_add_schedule(taxi_shuttle_control, mockserver, pgsql):
    response = await taxi_shuttle_control.put(
        '/admin/shuttle-control/v1/routes/item',
        json={
            'name': 'test route',
            'is_cyclic': False,
            'is_dynamic': False,
            'route': [
                {'point': [0, 0], 'is_stop': False},
                {'point': [0, 10], 'is_stop': False},
                {'point': [10, 10], 'is_stop': True, 'name': 'stop10'},
                {'point': [22, 12], 'is_stop': True, 'name': 'stop22'},
                {'point': [40, 40], 'is_stop': False},
                {'point': [42, 42], 'is_stop': True, 'name': 'stop42'},
            ],
            'schedule': {
                'timezone': 'UTC',
                'intervals': [{'exclude': False, 'day': [2, 5, 6, 7]}],
                'repeat': {'interval': 1800, 'origin': 'start'},
            },
        },
    )

    assert response.status_code == 200
    assert response.json() == {'route_id': 'Pmp80rQ23L4wZYxd'}

    rows = select_named(
        'SELECT route_id, name, is_deleted, version ' 'FROM config.routes',
        pgsql['shuttle_control'],
    )
    assert len(rows) == 2
    row = rows[0] if rows[0]['route_id'] == 2 else rows[1]
    assert row['name'] == 'test route'
    assert not row['is_deleted']
    assert row['version'] == 1

    rows = select_named(
        'SELECT crp.point_id, cp.position, crp.point_order,'
        'cs.stop_id, cs.name '
        'FROM config.route_points crp '
        'INNER JOIN config.points cp '
        'ON cp.point_id = crp.point_id '
        'LEFT JOIN config.stops cs '
        'ON cs.point_id = cp.point_id '
        'WHERE crp.route_id = 2 '
        'ORDER BY crp.point_id ASC',
        pgsql['shuttle_control'],
    )
    assert len(rows) == 6
    assert rows == [
        {
            'point_id': 2,
            'position': '(0,0)',
            'point_order': 1,
            'stop_id': None,
            'name': None,
        },
        {
            'point_id': 3,
            'position': '(0,10)',
            'point_order': 2,
            'stop_id': None,
            'name': None,
        },
        {
            'point_id': 4,
            'position': '(10,10)',
            'point_order': 3,
            'stop_id': 2,
            'name': 'stop10',
        },
        {
            'point_id': 5,
            'position': '(22,12)',
            'point_order': 4,
            'stop_id': 3,
            'name': 'stop22',
        },
        {
            'point_id': 6,
            'position': '(40,40)',
            'point_order': 5,
            'stop_id': None,
            'name': None,
        },
        {
            'point_id': 7,
            'position': '(42,42)',
            'point_order': 6,
            'stop_id': 4,
            'name': 'stop42',
        },
    ]


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'test route': {
            'driver': 'shuttle_control.routes.route.name_for_driver',
            'passenger': 'shuttle_control.routes.route.name_for_passenger',
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'shuttle_control.stops.stop0': {'ru': 'Остановка 0, 0'},
        'shuttle_control.stops.stop010': {'ru': 'Остановка 0, 10'},
        'shuttle_control.stops.stop10': {'ru': 'Остановка 10, 10'},
        'shuttle_control.stops.stop22': {'ru': 'Остановка 22, 12'},
        'shuttle_control.stops.stop40': {'ru': 'Остановка 40, 40'},
        'shuttle_control.stops.stop42': {'ru': 'Остановка 42, 42'},
        'shuttle_control.routes.route.name_for_driver': {
            'ru': 'Водительский маршрут',
        },
        'shuttle_control.routes.route.name_for_passenger': {
            'ru': 'Пассажирский маршрут',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
@pytest.mark.parametrize(
    'is_dynamic, is_cyclic, last_point, status_code',
    [
        (
            False,
            False,
            {'point': [42, 42], 'is_stop': True, 'name': 'stop42'},
            200,
        ),
        (False, False, {'point': [42, 42], 'is_stop': False}, 400),
        (
            False,
            True,
            {'point': [42, 42], 'is_stop': True, 'name': 'stop42'},
            200,
        ),
        (False, True, {'point': [42, 42], 'is_stop': False}, 200),
        (
            False,
            False,
            {'point': [42, 42], 'is_stop': True, 'name': 'stop42'},
            200,
        ),
        (
            False,
            False,
            {
                'point': [42, 42],
                'is_stop': True,
                'name': 'stop42',
                'is_required': False,
            },
            400,
        ),
        (
            True,
            False,
            {'point': [42, 42], 'is_stop': True, 'name': 'stop42'},
            200,
        ),
        (
            True,
            True,
            {'point': [42, 42], 'is_stop': True, 'name': 'stop42'},
            400,
        ),
        (True, False, {'point': [42, 42], 'is_stop': False}, 400),
        (
            True,
            False,
            {
                'point': [42, 42],
                'is_stop': True,
                'name': 'stop42',
                'is_required': False,
            },
            200,
        ),
    ],
)
async def test_add_cyclic_and_required(
        taxi_shuttle_control, is_dynamic, is_cyclic, last_point, status_code,
):
    # point, stop_name, is_required
    route_data = [
        ([0, 0], 'stop0' if is_dynamic else None, True),
        ([0, 10], 'stop010' if is_dynamic else None, True),
        ([10, 10], 'stop10', None),
        ([22, 12], 'stop22' if is_dynamic else None, None),
        ([40, 40], 'stop40' if is_dynamic else None, None),
    ]

    route = [
        _exclude_none(
            {
                'point': point,
                'is_stop': stop_name is not None,
                'name': stop_name,
                'is_required': is_required,
            },
        )
        for point, stop_name, is_required in route_data
    ]

    response = await taxi_shuttle_control.put(
        '/admin/shuttle-control/v1/routes/item',
        json={
            'name': 'test route',
            'is_cyclic': is_cyclic,
            'is_dynamic': is_dynamic,
            'route': route + [last_point],
        },
    )

    assert response.status_code == status_code


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'test route': {
            'driver': 'shuttle_control.routes.route.name_for_driver',
            'passenger': 'shuttle_control.routes.route.name_for_passenger',
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'shuttle_control.stops.stop10': {'ru': 'Остановка 10, 10'},
        'shuttle_control.stops.stop22': {'ru': 'Остановка 22, 12'},
        'shuttle_control.routes.route.name_for_driver_lol': {
            'ru': 'Водительский маршрут',
        },
        'shuttle_control.routes.route.name_for_passenger': {
            'ru': 'Пассажирский маршрут',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_without_tanker_driver_route_name(taxi_shuttle_control):
    response = await taxi_shuttle_control.put(
        '/admin/shuttle-control/v1/routes/item',
        json={
            'name': 'test route',
            'is_cyclic': True,
            'route': [
                {'point': [0, 0], 'is_stop': False},
                {'point': [0, 10], 'is_stop': False},
                {'point': [10, 10], 'is_stop': True, 'name': 'stop10'},
                {'point': [22, 12], 'is_stop': True, 'name': 'stop22'},
                {'point': [40, 40], 'is_stop': False},
            ],
        },
    )

    assert response.json() == {
        'code': '400',
        'message': (
            'Can\'t find tanker key '
            'shuttle_control.routes.route.name_for_driver '
            'for driver route name'
        ),
    }


@pytest.mark.config(
    SHUTTLE_CONTROL_ROUTE_TANKER_KEYS_BY_USER_TYPE={
        'test route': {
            'driver': 'shuttle_control.routes.route.name_for_driver',
            'passenger': 'shuttle_control.routes.route.name_for_passenger',
        },
    },
)
@pytest.mark.translations(
    client_messages={
        'shuttle_control.stops.stop10': {'ru': 'Остановка 10, 10'},
        'shuttle_control.stops.stop22_lol': {'ru': 'Остановка 22, 12'},
        'shuttle_control.routes.route.name_for_driver': {
            'ru': 'Водительский маршрут',
        },
        'shuttle_control.routes.route.name_for_passenger': {
            'ru': 'Пассажирский маршрут',
        },
    },
)
@pytest.mark.pgsql('shuttle_control', files=['main.sql'])
async def test_without_tanker_stop_name(taxi_shuttle_control):
    response = await taxi_shuttle_control.put(
        '/admin/shuttle-control/v1/routes/item',
        json={
            'name': 'test route',
            'is_cyclic': True,
            'route': [
                {'point': [0, 0], 'is_stop': False},
                {'point': [0, 10], 'is_stop': False},
                {'point': [10, 10], 'is_stop': True, 'name': 'stop10'},
                {'point': [22, 12], 'is_stop': True, 'name': 'stop22'},
                {'point': [40, 40], 'is_stop': False},
            ],
        },
    )

    assert response.json() == {
        'code': '400',
        'message': (
            'Can\'t find tanker key shuttle_control.stops.stop22 '
            'for stop stop22'
        ),
    }

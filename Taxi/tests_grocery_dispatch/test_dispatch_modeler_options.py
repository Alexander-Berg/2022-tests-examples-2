from tests_grocery_dispatch import constants as const

MODELER_OPTIONS_REQUEST = {
    'dispatch_modeler_options': [
        {'depot_id': const.DEPOT_ID, 'order_per_courier_val': 1.2},
        {'depot_id': '67890', 'order_per_courier_val': 1.3},
    ],
}

MODELER_OPTIONS_RESPONSE = [
    {'depot_id': const.DEPOT_ID, 'status': 'ok'},
    {'depot_id': '67890', 'status': 'not_found'},
]

DISPATCH_MODELER_OPTIONS_PG = [(const.DEPOT_ID, 1.2)]


async def test_basic_modeler_options(taxi_grocery_dispatch, pgsql):
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/modeler_options', MODELER_OPTIONS_REQUEST,
    )

    assert response.status == 200
    assert response.json() == MODELER_OPTIONS_RESPONSE

    cursor = pgsql['grocery_dispatch'].cursor()
    cursor.execute('SELECT * FROM dispatch.dispatch_modeler_options')
    result = cursor.fetchall()
    assert len(result) == 1
    assert result == DISPATCH_MODELER_OPTIONS_PG

from tests_grocery_dispatch import constants as const

MODELER_ETA_OPTIONS_REQUEST = {
    'eta_thresholds': [
        {'depot_id': const.DEPOT_ID, 'eta': 60},
        {'depot_id': '67890', 'eta': 70},
    ],
}

MODELER_ETA_OPTIONS_RESPONSE = [
    {'depot_id': const.DEPOT_ID, 'status': 'ok'},
    {'depot_id': '67890', 'status': 'not_found'},
]

DISPATCH_MODELER_OPTIONS_PG = [(const.DEPOT_ID, 60)]


async def test_basic_eta_modeler_options(taxi_grocery_dispatch, pgsql):
    response = await taxi_grocery_dispatch.post(
        '/internal/dispatch/v1/modeler_eta_options',
        MODELER_ETA_OPTIONS_REQUEST,
    )

    assert response.status == 200
    assert response.json() == MODELER_ETA_OPTIONS_RESPONSE

    cursor = pgsql['grocery_dispatch'].cursor()
    cursor.execute('SELECT * FROM dispatch.dispatch_eta_modeler_threshold')
    result = cursor.fetchall()
    assert len(result) == 1
    assert result == DISPATCH_MODELER_OPTIONS_PG

from . import experiments

LEGACY_DEPOT_ID = '100'
DEPOT_ID = 'test_depot_id'


def _prepare_depots(overlord_catalog, location, grocery_depots):
    overlord_catalog.add_location(
        location=location, depot_id=DEPOT_ID, legacy_depot_id=LEGACY_DEPOT_ID,
    )
    overlord_catalog.add_depot(
        depot_id=DEPOT_ID, legacy_depot_id=LEGACY_DEPOT_ID,
    )
    grocery_depots.add_depot(
        depot_test_id=int(LEGACY_DEPOT_ID),
        depot_id=DEPOT_ID,
        location=location,
    )


@experiments.GROCERY_API_ERRORS_CONFIG
async def test_errors_info_in_response(
        taxi_grocery_api, overlord_catalog, grocery_depots,
):
    location = [0, 0]
    _prepare_depots(overlord_catalog, location, grocery_depots)
    json = {'position': {'location': location}}
    headers = {'X-YaTaxi-Session': 'taxi: user-id', 'Accept-Language': 'en'}
    response = await taxi_grocery_api.post(
        '/lavka/v1/api/v1/errors-config', json=json, headers=headers,
    )
    response_json = response.json()
    assert response.status_code == 200
    assert response_json['errors_info'] == [
        {
            'name': 'test_informer',
            'text': 'hello',
            'text_color': 'blue',
            'background_color': 'blue',
            'disable_cart': True,
            'disable_cart_checkout': False,
            'modal': {
                'text': 'hello',
                'text_color': 'blue',
                'background_color': 'blue',
                'picture': 'some_picture',
                'title': 'some_title',
                'buttons': [
                    {
                        'variant': 'default',
                        'text': 'button',
                        'text_color': 'blue',
                        'background_color': 'blue',
                        'link': 'some_link',
                    },
                    {'variant': 'default', 'text': 'button too'},
                ],
            },
        },
    ]

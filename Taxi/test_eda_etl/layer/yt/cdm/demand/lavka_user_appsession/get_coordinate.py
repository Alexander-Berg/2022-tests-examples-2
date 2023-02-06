from eda_etl.layer.yt.cdm.demand.lavka_user_appsession.impl import get_coordinate


def test_get_coordinate():
    for input_event_value, input_event_name, expected in (
        ({},'', {'lat': None, 'lon': None}),
        (
            {'serviceeventvalue':{'coords': [44.0529903, 42.8452718]}},
            'Superapp.Showcase.Event.eda.map.address_selected',
            {'lat': 44.0529903, 'lon': 42.8452718}
        ),
        (
            {'serviceeventvalue': {'coords1': [44.0529903, 42.8452718]}},
            'Superapp.Showcase.Event.eda.map.address_selected',
            {'lat': None, 'lon': None}
        ),
        (
            {'suggest.pin_drop': {'coordinate': {'lat': 44.0529903, 'lon': 42.8452718}}},
            'Superapp.AddressChanged',
            {'lat': 44.0529903, 'lon': 42.8452718}
        ),
        (
            {'suggest.pin_drop': {'coordinate1': {'lat': 44.0529903, 'lon': 42.8452718}}},
            'Superapp.AddressChanged',
            {'lat': None, 'lon': None}
        ),
        (
            {'suggest.finalize': {'coordinate': {'lat': 44.0529903, 'lon': 42.8452718}}},
            'Superapp.AddressChanged',
            {'lat': 44.0529903, 'lon': 42.8452718}
        ),
        (
            {'suggest.finalize': {'coordinate1': {'lat': 44.0529903, 'lon': 42.8452718}}},
            'Superapp.AddressChanged',
            {'lat': None, 'lon': None}
        ),
        (
            {'suggest': {'coordinate': {'lat': 44.0529903, 'lon': 42.8452718}}},
            'Superapp.AddressChanged',
            {'lat': 44.0529903, 'lon': 42.8452718}
        ),
        (
            {'suggest': {'coordinate1': {'lat': 44.0529903, 'lon': 42.8452718}}},
            'Superapp.AddressChanged',
            {'lat': None, 'lon': None}
        ),
        (
            {'coordinate': {'lat': 44.0529903, 'lon': 42.8452718}},
            'Superapp.AddressChanged',
            {'lat': 44.0529903, 'lon': 42.8452718}
        ),
        (
            {'coordinate1': {'lat': 44.0529903, 'lon': 42.8452718}},
            'Superapp.AddressChanged',
            {'lat': None, 'lon': None}
        ),
        (
            {'address': {'coordinate': {'lat': 44.0529903, 'lon': 42.8452718}}},
            'address_search.ZeroSuggestSelectAddress',
            {'lat': 44.0529903, 'lon': 42.8452718}
        ),
        (
            {'address': {'coordinate1': {'lat': 44.0529903, 'lon': 42.8452718}}},
            'address_search.ZeroSuggestSelectAddress',
            {'lat': None, 'lon': None}
        ),
        (
            {'address': {'coordinate': {'lat': 44.0529903, 'lon': 42.8452718}}},
            'address_search.SuggestSelectAddress',
            {'lat': 44.0529903, 'lon': 42.8452718}
        ),
        (
            {'address': {'coordinate1': {'lat': 44.0529903, 'lon': 42.8452718}}},
            'address_search.SuggestSelectAddress',
            {'lat': None, 'lon': None}
        ),

    ):
        actual_lat = get_coordinate(input_event_name, input_event_value, 'lat')

        assert (expected['lat'] == actual_lat), \
            'Expected latitude is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected['lat'], actual_lat, input_event_value
            )

        actual_lon = get_coordinate(input_event_name, input_event_value, 'lon')

        assert (expected['lon'] == actual_lon), \
            'Expected longitude is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected['lon'], actual_lat, input_event_value
            )

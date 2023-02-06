from eda_etl.layer.yt.cdm.user_product.eda_user_appsession.impl import get_coordinate_from_url


def test_get_destination_lat():
    for input_dict, expected in (
        (None, {'latitude': None, 'longitude': None}),
        ('https://eda.yandex/api/v2/catalog?latitude=59.929276&longitude=30.347309',
            {'latitude': 59.929276, 'longitude': 30.347309}),
        ('https://eda.yandex/api/nev2/catalog?latitude=59.929276&longitude=30.347309',
            {'latitude': None, 'longitude': None}),
        ('https://eda.yandex/api/v2/catalog?search=Kfc&latitude=55.869612&sort=default&longitude=37.536823',
            {'latitude': 55.869612, 'longitude': 37.536823}),
        ('https://eda.yandex/api/v2/catalog?search=Kfc&latitude=abc&sort=default&longitude=def',
         {'latitude': None, 'longitude': None}),
    ):
        actual_lat = get_coordinate_from_url(input_dict, 'latitude')

        assert (expected['latitude'] == actual_lat), \
            'Expected latitude is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected['latitude'], actual_lat, input_dict
            )

        actual_lon = get_coordinate_from_url(input_dict, 'longitude')

        assert (expected['longitude'] == actual_lon), \
            'Expected longitude is different from actual:\nexpected: {},\nactual: {}\ntest sample: {}'.format(
                expected['longitude'], actual_lat, input_dict
            )

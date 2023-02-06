import pytest


@pytest.fixture(name='search_places_within_bbox')
def _search_places_within_bbox(taxi_eats_catalog_storage):
    async def _search_places_within_bbox(corners, **kwargs):
        body = {'bounding_box': corners, **kwargs}
        return await taxi_eats_catalog_storage.post(
            '/internal/eats-catalog-storage/v1/search/places-within-bbox',
            json=body,
        )

    return _search_places_within_bbox


PLACE_FIELDS = [
    'created_at',
    'updated_at',
    'slug',
    'enabled',
    'name',
    'revision',
    'type',
    'business',
    'launched_at',
    'payment_methods',
    'gallery',
    'brand',
    'address',
    'country',
    'categories',
    'quick_filters',
    'wizard_quick_filters',
    'region',
    'price_category',
    'assembly_cost',
    'rating',
    'extra_info',
    'features',
    'timing',
    'sorting',
    'address_comment',
    'contacts',
    'working_intervals',
    'allowed_couriers_types',
    'origin_id',
]

ZONE_FIELDS = [
    'source',
    'couriers_zone_id',
    'name',
    'created_at',
    'updated_at',
    'revision',
    'enabled',
    'couriers_type',
    'delivery_conditions',
    'market_avg_time',
    'arrival_time',
    'working_intervals',
    'polygons',
]


@pytest.fixture(name='insert_locations')
def _insert_locations(pgsql):
    def _insert_locations(locations):
        cursor = pgsql['eats_catalog_storage'].cursor()
        fields_str = ', '.join(PLACE_FIELDS)
        values_str = '%s, point(%s, %s), ' + fields_str
        fields_str = 'id, location, ' + fields_str

        for place_id, (lon, lat) in locations.items():
            cursor.execute(
                'INSERT INTO storage.places({0}) '
                '(SELECT {1} FROM storage.places LIMIT 1) '
                'ON CONFLICT(id) DO UPDATE '
                'SET id=EXCLUDED.id, '
                'location=EXCLUDED.location;'.format(fields_str, values_str),
                (place_id, lon, lat),
            )

    return _insert_locations


@pytest.fixture(name='insert_delivery_zones')
def _insert_delivery_zones(pgsql):
    def _insert_delivery_zones(place_to_zones):
        cursor = pgsql['eats_catalog_storage'].cursor()
        fields_str = ', '.join(ZONE_FIELDS)
        values_str = '%s, %s, %s, %s, ' + fields_str
        fields_str = 'id, external_id, place_id, shipping_type, ' + fields_str

        for place_id, zones in place_to_zones.items():
            for zone_id, shipping_type in zones:
                cursor.execute(
                    'INSERT INTO storage.delivery_zones({0}) '
                    '(SELECT {1} FROM storage.delivery_zones LIMIT 1) '
                    'ON CONFLICT(id) DO UPDATE '
                    'SET id=EXCLUDED.id, '
                    'shipping_type=EXCLUDED.shipping_type, '
                    'place_id=EXCLUDED.place_id;'.format(
                        fields_str, values_str,
                    ),
                    (zone_id, zone_id, place_id, shipping_type),
                )

    return _insert_delivery_zones


@pytest.fixture(name='disable_by_id')
def _disable_by_id(pgsql):
    def _disable_by_id(ids, relation_name):
        if not ids:
            return
        cursor = pgsql['eats_catalog_storage'].cursor()
        cursor.execute(
            'UPDATE storage.{} '
            'SET enabled = false '
            'WHERE id IN %s;'.format(relation_name),
            (tuple(ids),),
        )

    return _disable_by_id


def filter_points_within_bbox(bbox, locations):
    first, second = bbox
    lower_left = (min(first[0], second[0]), min(first[1], second[1]))
    upper_right = (max(first[0], second[0]), max(first[1], second[1]))

    within_bbox = set()
    for place_id, (x, y) in locations.items():
        if (
                lower_left[0] <= x <= upper_right[0]
                and lower_left[1] <= y <= upper_right[1]
        ):
            within_bbox.add(place_id)

    return within_bbox


@pytest.mark.parametrize(
    'bounding_box',
    [
        pytest.param([[37, 55], [38, 56]], id='lower_left__upper_right'),
        pytest.param([[38, 56], [37, 55]], id='upper_right__lower_left'),
        pytest.param([[38, 55], [37, 56]], id='lower_right__upper_left'),
        pytest.param([[37, 56], [38, 55]], id='upper_left__lower_right'),
    ],
)
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_places_within_bbox(
        search_places_within_bbox,
        insert_locations,
        bounding_box,
        insert_delivery_zones,
):
    points = [
        [37, 55],
        [38, 56],
        [10, 20],
        [36, 55.5],
        [37.5, 57],
        [37.1, 55.1],
    ]
    locations = {i: point for i, point in enumerate(points)}
    insert_locations(locations)
    insert_delivery_zones({i: [(i, 'delivery')] for i in locations.keys()})

    response = await search_places_within_bbox(bounding_box)
    assert response.status_code == 200

    places = response.json()['places']
    assert set(place['id'] for place in places) == filter_points_within_bbox(
        bounding_box, locations,
    )


@pytest.mark.parametrize(
    'disabled_places, disabled_zones, shipping_type, expected_json',
    [
        pytest.param(
            [],
            [],
            'pickup',
            [
                {'id': 0, 'zone_ids': [1]},
                {'id': 5, 'zone_ids': [15, 16]},
                {'id': 6, 'zone_ids': [18]},
                {'id': 7, 'zone_ids': [21]},
            ],
        ),
        pytest.param(
            [0, 1],
            [0, 15, 18],
            'pickup',
            [{'id': 5, 'zone_ids': [16]}, {'id': 7, 'zone_ids': [21]}],
        ),
        pytest.param(
            [],
            [],
            'delivery',
            [
                {'id': 0, 'zone_ids': [2, 0]},
                {'id': 1, 'zone_ids': [3]},
                {'id': 3, 'zone_ids': [10, 9]},
                {'id': 7, 'zone_ids': [22]},
            ],
        ),
        pytest.param(
            [0, 1],
            [0, 15, 18],
            'delivery',
            [{'id': 3, 'zone_ids': [10, 9]}, {'id': 7, 'zone_ids': [22]}],
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_catalog_storage', files=['insert_places_and_zones.sql'],
)
async def test_search_places_wit_zones(
        search_places_within_bbox,
        insert_locations,
        insert_delivery_zones,
        disable_by_id,
        disabled_places,
        disabled_zones,
        shipping_type,
        expected_json,
):
    bounding_box = [[37, 55], [38, 56]]
    points = {
        # place_id: (location, [zones])
        0: ([37, 55], ['delivery', 'pickup', 'delivery']),  # 0, 1, 2
        1: ([38, 56], ['delivery']),  # 3
        2: ([10, 20], ['pickup', 'delivery']),  # 6, 7, 8
        3: ([37.01, 55.01], ['delivery', 'delivery']),  # 9, 10
        4: ([37.5, 57], ['delivery', 'pickup']),  # 12, 13
        5: ([37.1, 55.1], ['pickup', 'pickup']),  # 15, 16
        6: ([37.5, 55.5], ['pickup']),  # 18
        7: ([38, 56], ['pickup', 'delivery']),  # 21, 22
    }
    locations = {i: point[0] for i, point in points.items()}
    insert_locations(locations)

    max_zones = max(len(zones) for _, zones in points.values())
    zones = {
        i: [(i * max_zones + j, type_) for j, type_ in enumerate(point[1])]
        for i, point in points.items()
    }
    insert_delivery_zones(zones)

    disable_by_id(disabled_places, 'places')
    disable_by_id(disabled_zones, 'delivery_zones')

    response = await search_places_within_bbox(
        bounding_box, shipping_type=shipping_type,
    )
    assert response.status_code == 200

    places: list = response.json()['places']
    assert len(places) == len(expected_json)
    for actual_place, expected_place in zip(places, expected_json):
        assert actual_place['id'] == expected_place['id']
        assert set(actual_place['zone_ids']) == set(expected_place['zone_ids'])

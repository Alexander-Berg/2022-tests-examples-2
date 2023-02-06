import datetime
import itertools

import pytest

BASE_URL = '/v1/admin/shortcuts/eats'
BASE_IMAGES_URL = 'https://tc.mobile.yandex.net/static/images'


DEFAULT_EATS_IMAGE_TAG = 'shortcuts_eats_place_default'
DEFAULT_EATS_PLACE = {
    'address_city': 'Moscow',
    'brand_id': 1,
    'lat': 1.00,
    'lon': 1.00,
    'name': f'test_name',
    'place_id': 10,
    'category_id': 20,
    'rating': 5.0,
    'slug': f'test_slug',
    'price_category_id': 1,
}

DEFAULT_OVERRIDE = {
    'title': 'default_title',
    'image_tags': [DEFAULT_EATS_IMAGE_TAG],
}


def generate_eats_place(x, name=None, brand_id=None):
    return {
        **DEFAULT_EATS_PLACE,
        'name': name or f'test_name_{x}',
        'brand_id': brand_id if brand_id is not None else x,
        'place_id': 10 + x,
        'category_id': 20 + x,
        'slug': f'test_slug_{x}',
    }


EATS_PLACES = [generate_eats_place(x) for x in range(1, 4)]


def get_eats_update_payload(brand_id=101, image_tags=None, title=None):
    payload = {'brand_id': brand_id}
    if image_tags:
        payload['image_tags'] = image_tags
    if title:
        payload['title'] = title

    return payload


def build_insert_query(eats_places):
    def build_value(value):
        return (
            f'('
            f'\'{value["address_city"]}\', \'{value["brand_id"]}\','
            f'  {value["lat"]},              {value["lon"]},'
            f'\'{value["name"]}\',           {value["place_id"]},'
            f'  {value["category_id"]},      {value["rating"]},'
            f'\'{value["slug"]}\',         \'{value["price_category_id"]}\''
            f')'
        )

    values = ', '.join([build_value(i) for i in eats_places])
    return f'INSERT INTO shortcuts_admin.eats_places VALUES {values}'


def fill_db(pgsql, eats_places):
    cursor = pgsql['shortcuts_admin'].cursor()
    cursor.execute(build_insert_query(eats_places))


@pytest.mark.config(
    SHORTCUTS_ADMIN_CONSTANTS={
        'default_eats_shortcut_color': '#AABBCC',
        'default_eats_shortcut_image_tag': 'default_image_tag',
        'eats_brand_black_list': [3, 12],
        'default_grocery_shortcut_color': '',  # not used
    },
)
async def test_list(taxi_shortcuts_admin, pgsql):
    fill_db(pgsql, EATS_PLACES)

    response = await taxi_shortcuts_admin.get(f'{BASE_URL}/list')
    assert response.status_code == 200
    shortcuts = response.json().get('shortcuts')

    allowed_eats_places = [
        ep for ep in EATS_PLACES if ep['brand_id'] not in [3, 12]
    ]
    assert len(shortcuts) == len(allowed_eats_places)
    for shortcut, eats_place in zip(shortcuts, allowed_eats_places):
        assert shortcut['title'] == eats_place['name']
        assert shortcut['place_id'] == eats_place['place_id']
        assert shortcut['slug'] == eats_place['slug']
        assert shortcut['color'] == '#AABBCC'
        assert shortcut['image_tag'] == 'default_image_tag'
        assert shortcut['rating'] == eats_place['rating']
        assert shortcut['price_category'] == eats_place['price_category_id']
        assert shortcut['brand_id'] == eats_place['brand_id']


async def test_list_no_price_category(taxi_shortcuts_admin, pgsql):
    fill_db(pgsql, [{**DEFAULT_EATS_PLACE, 'price_category_id': -1}])

    response = await taxi_shortcuts_admin.get(f'{BASE_URL}/list')
    assert response.status_code == 200
    shortcuts = response.json().get('shortcuts')

    assert len(shortcuts) == 1
    assert 'price_category' not in shortcuts[0]


@pytest.mark.parametrize('update_by, id_', [('brand', 2), ('category', 23)])
@pytest.mark.parametrize(
    'overrides',
    [
        {'image_tags': ['tag_1', 'tag_2'], 'title': 'my_pretty_title'},
        {'image_tags': ['tag_3']},
        {'title': 'my_pretty_title'},
    ],
)
async def test_use_override(
        taxi_shortcuts_admin, find_shortcuts, update_by, id_, overrides, pgsql,
):
    fill_db(pgsql, EATS_PLACES)

    response = await taxi_shortcuts_admin.post(
        f'{BASE_URL}/update-{update_by}',
        json={f'{update_by}_id': id_, **overrides},
    )
    assert response.status_code == 200

    response = await taxi_shortcuts_admin.get(f'{BASE_URL}/list')
    assert response.status_code == 200
    shortcuts = response.json()['shortcuts']

    modified_shortcuts = find_shortcuts(
        shortcuts, EATS_PLACES, **{f'{update_by}_id': id_},
    )
    assert len(modified_shortcuts) >= 1

    eats_place = [ep for ep in EATS_PLACES if ep[f'{update_by}_id'] == id_][0]
    expected_title = overrides.get('title', eats_place['name'])
    assert modified_shortcuts[0]['title'] == expected_title

    expected_image_tags = overrides.get('image_tags', [DEFAULT_EATS_IMAGE_TAG])
    assert modified_shortcuts[0]['image_tags'] == expected_image_tags
    # backward compatibility
    assert modified_shortcuts[0]['image_tag'] == expected_image_tags[0]


@pytest.mark.parametrize(
    'non_empty_fields', [['title', 'image_tags'], ['title'], ['image_tags']],
)
async def test_brands_info_appearance_update(
        taxi_shortcuts_admin, pgsql, non_empty_fields,
):
    fill_db(pgsql, EATS_PLACES)

    default_appearance_overrides = [
        get_eats_update_payload(
            brand_id=eats_place['brand_id'],
            **{
                k: v
                for (k, v) in DEFAULT_OVERRIDE.items()
                if k in non_empty_fields
            },
        )
        for eats_place in EATS_PLACES
    ]
    for override in default_appearance_overrides:
        response = await taxi_shortcuts_admin.post(
            f'{BASE_URL}/update-brand', override,
        )
        assert response.status_code == 200

    response = await taxi_shortcuts_admin.get(f'{BASE_URL}/brands-info')
    assert response.status_code == 200
    data = response.json()['data']

    assert len(data) == len(default_appearance_overrides)
    for (res, override) in zip(data, default_appearance_overrides):
        assert res['brand_id'] == override['brand_id']
        # compare None's if tags/titles do not exist in database
        assert res.get('image_tags') == override.get('image_tags')
        assert res.get('title') == override.get('title')
        assert res['autoupdate_enabled'] == override.get(
            'autoupdate_enabled', True,
        )
        appearance_updated_at = datetime.datetime.strptime(
            res['appearance_updated_at'], '%Y-%m-%dT%H:%M:%S.%f%z',
        )
        assert (
            datetime.datetime.now(datetime.timezone.utc)
            - appearance_updated_at
        ) < datetime.timedelta(minutes=1)


async def test_brands_info(taxi_shortcuts_admin, pgsql):
    number_generator = itertools.count()
    test_places = []
    # Two places with same brand but without appearance override
    aoless_brand_id = 1
    test_places.extend(
        [
            generate_eats_place(
                x=next(number_generator), brand_id=aoless_brand_id,
            )
            for _ in range(2)
        ],
    )
    # Two places with same brand and appearance override
    ao_brand_id = 2
    test_places.extend(
        [
            generate_eats_place(x=next(number_generator), brand_id=ao_brand_id)
            for _ in range(2)
        ],
    )
    fill_db(pgsql, test_places)
    override = get_eats_update_payload(
        brand_id=ao_brand_id, **DEFAULT_OVERRIDE,
    )
    response = await taxi_shortcuts_admin.post(
        f'{BASE_URL}/update-brand', override,
    )
    assert response.status_code == 200

    expected_results = {
        aoless_brand_id: {'image_tags': None, 'title': None},
        ao_brand_id: {
            'image_tags': override['image_tags'],
            'title': override['title'],
        },
    }

    response = await taxi_shortcuts_admin.get(f'{BASE_URL}/brands-info')
    assert response.status_code == 200
    data = response.json()['data']

    # should be equal to amount of brands
    assert len(data) == len(set(place['brand_id'] for place in test_places))

    for res in data:
        brand_id = res['brand_id']
        expected = expected_results[brand_id]
        # compare None's if tags/titles do not exist in database
        assert res.get('image_tags') == expected['image_tags']
        assert res.get('title') == expected['title']
        assert res['autoupdate_enabled']
        appearance_updated_at = datetime.datetime.strptime(
            res['appearance_updated_at'], '%Y-%m-%dT%H:%M:%S.%f%z',
        )
        zero_ts = datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
        should_have_zero_ts = brand_id == aoless_brand_id
        is_zero_ts = appearance_updated_at == zero_ts
        assert should_have_zero_ts == is_zero_ts


@pytest.mark.parametrize('validate_image_tags', [True, False])
@pytest.mark.parametrize('endpoint', ['update-brand', 'autoupdate-brand'])
async def test_image_tags_validation(
        taxi_shortcuts_admin, taxi_config, validate_image_tags, endpoint,
):
    taxi_config.set_values(
        {'SHORTCUTS_ADMIN_VALIDATE_IMAGE_TAGS': validate_image_tags},
    )

    response = await taxi_shortcuts_admin.post(
        f'{BASE_URL}/{endpoint}',
        get_eats_update_payload(image_tags=['non_existing_tag']),
    )
    assert response.status_code == 400 if validate_image_tags else 200


@pytest.mark.parametrize('autoupdate_enabled', [True, False])
async def test_update_brand(
        taxi_shortcuts_admin, pgsql, find_shortcuts, autoupdate_enabled,
):
    fill_db(pgsql, EATS_PLACES)
    for eats_place in EATS_PLACES:
        payload = {
            **get_eats_update_payload(brand_id=eats_place['brand_id']),
            **DEFAULT_OVERRIDE,
            'autoupdate_enabled': autoupdate_enabled,
        }
        # manual update
        response = await taxi_shortcuts_admin.post(
            f'{BASE_URL}/update-brand', payload,
        )
        assert response.status_code == 200

    payload = get_eats_update_payload(
        brand_id=1, image_tags=['tag_3'], title='new_title',
    )
    response = await taxi_shortcuts_admin.post(
        f'{BASE_URL}/autoupdate-brand', payload,
    )
    expected_status_code = 200 if autoupdate_enabled else 400
    assert response.status_code == expected_status_code

    if autoupdate_enabled:
        response = await taxi_shortcuts_admin.get(f'{BASE_URL}/list')
        assert response.status_code == 200
        shortcuts = response.json().get('shortcuts')

        modified_shortcuts = find_shortcuts(
            shortcuts, EATS_PLACES, **{'brand_id': 1},
        )
        assert len(modified_shortcuts) == 1
        assert modified_shortcuts[0]['title'] == 'new_title'
        assert modified_shortcuts[0]['image_tags'] == ['tag_3']
    else:
        assert response.json()['message'] == 'Automatic update forbidden'


@pytest.mark.parametrize(
    'overridden_fields',
    [[], ['title'], ['image_tags'], ['title', 'image_tags']],
)
async def test_upsert_brand_override(
        taxi_shortcuts_admin, pgsql, overridden_fields,
):
    def get_brand_overrides_from_pg(_cursor):
        _cursor.execute(
            """
                SELECT ebs.brand_id, ao.image_tags, ao.title
                FROM shortcuts_admin.appearance_overrides ao
                JOIN shortcuts_admin.eats_brand_settings ebs
                ON ebs.appearance_id = ao.appearance_id
            """,
        )
        return _cursor.fetchall()

    def get_brand_appearance_updated_at(_cursor):
        _cursor.execute(
            """
                SELECT ao.updated_at
                FROM shortcuts_admin.appearance_overrides ao
                JOIN shortcuts_admin.eats_brand_settings ebs
                    ON ebs.appearance_id = ao.appearance_id
            """,
        )
        return _cursor.fetchone()[0]

    cursor = pgsql['shortcuts_admin'].cursor()

    default_payload = get_eats_update_payload(**DEFAULT_OVERRIDE)
    response = await taxi_shortcuts_admin.post(
        f'{BASE_URL}/update-brand', default_payload,
    )
    assert response.status_code == 200

    overrides = get_brand_overrides_from_pg(cursor)
    assert len(overrides) == 1
    assert overrides[0] == tuple(default_payload.values())

    new_override = {
        'image_tags': ['tag_1', 'tag_2'],
        'title': 'test_title_new',
    }
    new_payload = get_eats_update_payload(
        **{k: v for (k, v) in new_override.items() if k in overridden_fields},
    )

    response = await taxi_shortcuts_admin.post(
        f'{BASE_URL}/update-brand', new_payload,
    )
    assert response.status_code == 200

    overrides = get_brand_overrides_from_pg(cursor)
    assert len(overrides) == 1
    actual_brand_id, actual_image_tags, actual_title = overrides[0]

    expected_override = {**DEFAULT_OVERRIDE, **new_payload}

    assert actual_brand_id == expected_override['brand_id']
    assert actual_title == expected_override['title']
    assert actual_image_tags == expected_override['image_tags']

    assert (
        datetime.datetime.now(datetime.timezone.utc)
        - get_brand_appearance_updated_at(cursor)
    ) < datetime.timedelta(minutes=1)


@pytest.mark.parametrize(
    'limit, offset',
    [
        pytest.param(2, 1),  # regular
        pytest.param(3, 0),  # no offset
        pytest.param(4, 1),  # offset + limit > end
        pytest.param(2, 5),  # offset > end
    ],
)
async def test_search_pagination(taxi_shortcuts_admin, pgsql, limit, offset):
    fill_db(pgsql, EATS_PLACES)
    response = await taxi_shortcuts_admin.post(
        f'{BASE_URL}/search', json={'limit': limit, 'offset': offset},
    )
    if offset >= len(EATS_PLACES):
        assert response.status_code == 500
        return

    assert response.status_code == 200

    data = response.json()
    shortcuts = data.get('shortcuts')
    assert data.get('total_size') == len(EATS_PLACES)

    eats_places_subset = EATS_PLACES[
        offset : min(offset + limit, len(EATS_PLACES))
    ]

    assert len(shortcuts) == len(eats_places_subset)
    for shortcut, eats_place in zip(shortcuts, eats_places_subset):
        assert shortcut['title'] == eats_place['name']
        assert shortcut['place_id'] == eats_place['place_id']
        assert shortcut['slug'] == eats_place['slug']


async def test_search_with_urls(taxi_shortcuts_admin, pgsql):
    fill_db(pgsql, EATS_PLACES)

    overridden_brand = 2
    response = await taxi_shortcuts_admin.post(
        f'{BASE_URL}/update-brand',
        get_eats_update_payload(
            brand_id=overridden_brand, image_tags=['tag_1', 'tag_2'],
        ),
    )
    assert response.status_code == 200

    response = await taxi_shortcuts_admin.post(
        f'{BASE_URL}/search', json={'limit': 10, 'offset': 0},
    )
    assert response.status_code == 200
    data = response.json()
    assert data.get('total_size') == len(EATS_PLACES)

    for shortcut, eats_place in zip(data['shortcuts'], EATS_PLACES):
        expected_image_urls = (
            [
                {
                    'image_tag': 'tag_1',
                    'image_url': f'{BASE_IMAGES_URL}/image_1',
                },
                {
                    'image_tag': 'tag_2',
                    'image_url': f'{BASE_IMAGES_URL}/image_2',
                },
            ]
            if eats_place['brand_id'] == overridden_brand
            else [
                {
                    'image_tag': 'shortcuts_eats_place_default',
                    'image_url': f'{BASE_IMAGES_URL}/image_0',
                },
            ]
        )
        assert shortcut['image_urls'] == expected_image_urls


async def test_search_by_brands(taxi_shortcuts_admin, pgsql):
    fill_db(pgsql, EATS_PLACES)

    brands = [EATS_PLACES[0]['brand_id'], EATS_PLACES[1]['brand_id']]
    response = await taxi_shortcuts_admin.post(
        f'{BASE_URL}/search',
        json={'brands': brands, 'limit': 10, 'offset': 0},
    )
    assert response.status_code == 200

    data = response.json()
    shortcuts = data.get('shortcuts')
    for i, shortcut in enumerate(shortcuts):
        assert shortcut['title'] == EATS_PLACES[i]['name']


@pytest.mark.parametrize('limit', [3, 50])
async def test_brands_list(taxi_shortcuts_admin, pgsql, limit):
    similar_names = ['Бургер Кинг', 'Бургерные герои', 'Бургеры']
    eats_places = EATS_PLACES + [
        generate_eats_place(10 + brand_id, name)
        for brand_id, name in enumerate(similar_names)
    ]
    fill_db(pgsql, eats_places)

    response = await taxi_shortcuts_admin.get(
        f'{BASE_URL}/brands-list', params={'token': 'бур', 'limit': limit},
    )
    assert response.status_code == 200

    brands = response.json()['brands']
    assert len(brands) <= min(limit, len(eats_places))

    titles = [brand['title'] for brand in brands]
    assert sorted(titles[: len(similar_names)]) == sorted(similar_names)

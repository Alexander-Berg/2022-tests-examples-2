import pytest

GET_CHILDREN_HANDLER = '/v1/place/categories/get_children'


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_404_unknown_place(taxi_eats_nomenclature):
    unknown_place_id = 9999

    response = await taxi_eats_nomenclature.post(
        f'{GET_CHILDREN_HANDLER}?place_id={unknown_place_id}',
        json={'category_ids': []},
    )

    assert response.status == 404


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_404_no_brand(taxi_eats_nomenclature, sql_delete_brand_place):
    place_id = 1

    sql_delete_brand_place(place_id)

    response = await taxi_eats_nomenclature.post(
        f'{GET_CHILDREN_HANDLER}?place_id={place_id}',
        json={'category_ids': []},
    )

    assert response.status == 404


@pytest.mark.parametrize(
    'use_exp, exp_assortment_name',
    [
        pytest.param(False, '', id='default assortment'),
        pytest.param(True, 'assortment_name_2', id='exp assortment'),
    ],
)
@pytest.mark.parametrize(
    'requested_assortment_name',
    [None, 'assortment_name_1', 'assortment_name_2'],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_assortment_name(
        taxi_eats_nomenclature,
        load_json,
        set_assortment_name_exp,
        # parametrize
        use_exp,
        exp_assortment_name,
        requested_assortment_name,
):
    set_assortment_name_exp(use_exp, exp_assortment_name)

    place_id = 1

    if requested_assortment_name is not None:
        expected_assortment_name = requested_assortment_name
    elif use_exp:
        expected_assortment_name = exp_assortment_name
    else:
        expected_assortment_name = 'assortment_name_1'

    if expected_assortment_name == 'assortment_name_1':
        response_file = 'response_1.json'
    elif expected_assortment_name == 'assortment_name_2':
        response_file = 'response_2.json'
    else:
        assert False, 'Forgot to add corresponding response?'

    expected_response = load_json(response_file)

    request = f'{GET_CHILDREN_HANDLER}?place_id={place_id}'
    if requested_assortment_name is not None:
        request += f'&assortment_name={requested_assortment_name}'

    response = await taxi_eats_nomenclature.post(
        request, json={'category_ids': []},
    )
    assert response.status == 200
    assert sorted_response_json(response.json()) == sorted_response_json(
        expected_response,
    )


@pytest.mark.parametrize(
    'exp_brand_ids, exp_excluded_place_ids, response_file',
    [
        pytest.param([1], [], 'response_2.json', id='exp assortment'),
        pytest.param(
            [1],
            [1],
            'response_1.json',
            id='default assortment: place in excluded places',
        ),
        pytest.param(
            [2],
            [],
            'response_1.json',
            id='default assortment: brand not in exp brands',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_assortment_name_exp_brand_and_place(
        taxi_eats_nomenclature,
        load_json,
        set_assortment_name_exp,
        # parametrize
        exp_brand_ids,
        exp_excluded_place_ids,
        response_file,
):
    set_assortment_name_exp(
        experiment_on=True,
        assortment_name='assortment_name_2',
        brand_ids=exp_brand_ids,
        excluded_place_ids=exp_excluded_place_ids,
    )

    place_id = 1

    requested_ids = ['22', '66']
    expected_response = load_json(response_file)
    filter_response(expected_response, None, requested_ids)

    request = f'{GET_CHILDREN_HANDLER}?place_id={place_id}'

    response = await taxi_eats_nomenclature.post(
        request, json={'category_ids': requested_ids},
    )
    assert response.status == 200
    assert sorted_response_json(response.json()) == sorted_response_json(
        expected_response,
    )


@pytest.mark.parametrize(
    'requested_ids',
    [
        pytest.param([], id='all categories'),
        pytest.param(['9999999', '11'], id='unknown category'),
        pytest.param(['11', '77'], id='different branches'),
        pytest.param(['11', '66'], id='same branch'),
        pytest.param(['55', '88'], id='leafs'),
    ],
)
@pytest.mark.parametrize('max_depth', [None, 0, 1, 2, 100])
@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_place_data.sql'],
)
async def test_filter_by_depth_and_ids(
        taxi_eats_nomenclature,
        load_json,
        # parametrize
        max_depth,
        requested_ids,
):
    place_id = 1

    expected_response = load_json('response_1.json')
    filter_response(expected_response, max_depth, requested_ids)

    request = f'{GET_CHILDREN_HANDLER}?place_id={place_id}'
    if max_depth is not None:
        request += f'&max_depth={max_depth}'

    response = await taxi_eats_nomenclature.post(
        request, json={'category_ids': requested_ids},
    )
    assert response.status == 200
    assert sorted_response_json(response.json()) == sorted_response_json(
        expected_response,
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_tags_test.sql'],
)
async def test_tags(taxi_eats_nomenclature, load_json):
    place_id = 1
    category_id = '11'

    expected_response = load_json('response_with_tags.json')

    request = f'{GET_CHILDREN_HANDLER}?place_id={place_id}'

    response = await taxi_eats_nomenclature.post(
        request, json={'category_ids': [category_id]},
    )
    assert response.status == 200
    assert sorted_response_json(response.json()) == sorted_response_json(
        expected_response,
    )


@pytest.mark.pgsql(
    'eats_nomenclature',
    files=['fill_dictionaries.sql', 'fill_data_for_test_category_types.sql'],
)
@pytest.mark.parametrize(
    'category_to_request, expected_type',
    [
        pytest.param('11', 'partner', id='partner'),
        pytest.param('22', 'custom_promo', id='custom_promo'),
        pytest.param('33', 'custom_base', id='custom_base'),
        pytest.param('44', 'custom_restaurant', id='custom_restaurant'),
    ],
)
async def test_category_types(
        taxi_eats_nomenclature,
        # parametrize
        category_to_request,
        expected_type,
):
    place_id = 1

    request = f'{GET_CHILDREN_HANDLER}?place_id={place_id}'

    response = await taxi_eats_nomenclature.post(
        request, json={'category_ids': [category_to_request]},
    )
    assert response.status == 200
    assert response.json()['categories'][0]['type'] == expected_type


def filter_response(response_json, max_depth, requested_ids):
    if max_depth is None:
        max_depth = 9999
    if requested_ids:
        root_ids = requested_ids
    else:
        root_ids = [
            c['id']
            for c in response_json['categories']
            if 'parent_id' not in c
        ]

    id_to_category = {c['id']: c for c in response_json['categories']}
    ids_to_return = set()
    ids_to_traverse = set(root_ids)

    for _ in range(0, max_depth + 1):
        new_ids_to_traverse = set()
        for cur_id in ids_to_traverse:
            if cur_id in ids_to_return or cur_id not in id_to_category:
                continue

            ids_to_return.add(cur_id)

            for child_id in id_to_category[cur_id]['child_ids']:
                if child_id in ids_to_return:
                    continue

                new_ids_to_traverse.add(child_id)

        ids_to_traverse = new_ids_to_traverse

    response_json['categories'] = [id_to_category[id] for id in ids_to_return]


def sorted_response_json(response_json):
    for category in response_json['categories']:
        category['child_ids'].sort()
        category['products'].sort(key=lambda product: product['id'])
    response_json['categories'].sort(key=lambda category: category['id'])

    return response_json

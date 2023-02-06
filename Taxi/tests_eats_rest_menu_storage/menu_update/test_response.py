import pytest

HANDLER = '/internal/v1/update/menu'


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_404(taxi_eats_rest_menu_storage, load_json):
    request = load_json('request.json')
    request['place_id'] = 123
    response = await taxi_eats_rest_menu_storage.post(HANDLER, json=request)
    assert response.status_code == 404


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_main_data.sql'])
async def test_200_no_previous_assortment(
        taxi_eats_rest_menu_storage, load_json,
):
    response = await taxi_eats_rest_menu_storage.post(
        HANDLER, json=load_json('request.json'),
    )
    assert response.status_code == 200


@pytest.mark.pgsql('eats_rest_menu_storage', files=['fill_data.sql'])
async def test_200(
        taxi_eats_rest_menu_storage, load_json, assert_response_data,
):
    request = load_json('request.json')
    response = await taxi_eats_rest_menu_storage.post(HANDLER, json=request)
    assert response.status_code == 200
    data = response.json()

    expected_items = {
        'item_origin_id_2',
        'item_origin_id_3',
        'item_origin_id_4',
        'item_origin_id_5',
        'item_origin_id_6',
    }
    expected_inner_options = {
        'inner_option_origin_id_1',
        'inner_option_origin_id_2',
        'inner_option_origin_id_6',
    }
    expected_option_groups = {
        'option_group_origin_id_1',
        'option_group_origin_id_2',
        'option_group_origin_id_6',
    }
    expected_options = {
        'option_origin_id_1',
        'option_origin_id_2',
        'option_origin_id_1',
        'option_origin_id_3',
    }
    expected_categories = {
        'category_origin_id_10',
        'category_origin_id_2',
        'category_origin_id_3',
        'category_origin_id_4',
        'category_origin_id_5',
        'category_origin_id_9',
    }
    assert_response_data(data['items'], 'place_menu_items', expected_items)
    assert_response_data(
        data['inner_options'],
        'place_menu_item_inner_options',
        expected_inner_options,
    )
    assert_response_data(
        data['options_groups'],
        'place_menu_item_option_groups',
        expected_option_groups,
    )
    assert_response_data(
        data['options'], 'place_menu_item_options', expected_options,
    )
    assert_response_data(
        data['categories'], 'place_menu_categories', expected_categories,
    )


@pytest.fixture(name='assert_response_data')
def _assert_response_data(sql_uuid_origin_id_mapping):
    def do_assert_response_data(
            response_items, table_name, expected_origin_ids,
    ):
        uuid_to_origin_id = sql_uuid_origin_id_mapping(table_name=table_name)
        response_origin_ids = set()
        for item in response_items:
            assert item['id'] in uuid_to_origin_id
            assert uuid_to_origin_id[item['id']] == item['origin_id']
            response_origin_ids.add(item['origin_id'])
        assert expected_origin_ids == response_origin_ids

    return do_assert_response_data

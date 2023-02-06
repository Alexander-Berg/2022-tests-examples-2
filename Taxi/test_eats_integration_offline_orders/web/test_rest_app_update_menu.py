import pytest

from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    'partner_id,place_id, expected_status, expected_answer, '
    'access_check_result, expected_db_updates, request_menu,'
    'expected_deleted_counter, delete_images',
    [
        pytest.param(
            '10',
            3,
            400,
            {'message': 'Rest app request error', 'code': 'resp_app_error'},
            400,
            '{}',
            conftest.FULL_MENU_UPDATES,
            0,
            [],
            id='rest app error',
        ),
        pytest.param(
            '10',
            3,
            403,
            {'message': 'Access denied', 'code': 'no_access'},
            403,
            '{}',
            conftest.FULL_MENU_UPDATES,
            0,
            [],
            id='access denied',
        ),
        pytest.param(
            '10',
            10,
            404,
            {'message': 'No menu found', 'code': 'no_menu'},
            200,
            conftest.BASE_MENU,
            conftest.BASE_MENU,
            0,
            [],
            id='no place',
        ),
        pytest.param(
            '1',
            1,
            200,
            None,
            200,
            '{"items": {}, "categories": {}}',
            conftest.BASE_MENU,
            0,
            [],
            id='base menu only',
        ),
        pytest.param(
            '1',
            2,
            200,
            None,
            200,
            '{"items": '
            '{"menu_item_id__1": '
            '{"vat": 10, '
            '"title": "Булочка", '
            '"measure": 200.0, '
            '"sort_order": 150, '
            '"description": "с изюмом", '
            '"measure_unit": "Грамм"}}, '
            '"categories": {}}',
            conftest.PARTLY_UPDATED_MENU,
            0,
            [],
            id='partly update, rewrite images, title, description',
        ),
        pytest.param(
            '1',
            3,
            200,
            None,
            200,
            '{"items": '
            '{"menu_item_id__1": {'
            '"vat": 10, '
            '"measure": 200.0, '
            '"nutrients": {'
            '"fats": "3.6", '
            '"calories": "1.0", '
            '"proteins": "2.3", '
            '"carbohydrates": "50"}, '
            '"sort_order": 150, '
            '"measure_unit": "Грамм", '
            '"restapp_image_ids": ["1/image1", "1/image2"]}}, '
            '"categories": {"menu_category_id__1": {"sort_order": 160}}}',
            conftest.FULL_MENU_UPDATES,
            1,
            [{'url': 'path/1/image1', 'image_id': '1/image1'}],
            id='full update',
        ),
    ],
)
@pytest.mark.pgsql(
    'eats_integration_offline_orders', files=['restaurants.sql', 'menu.sql'],
)
@pytest.mark.config(
    TVM_RULES=[
        {
            'src': 'eats-integration-offline-orders',
            'dst': 'eats-restapp-authorizer',
        },
    ],
)
async def test_update_menu_restapp(
        web_app_client,
        web_context,
        patch,
        mockserver,
        partner_id,
        place_id,
        expected_status,
        expected_answer,
        access_check_result,
        expected_db_updates,
        request_menu,
        expected_deleted_counter,
        delete_images,
):
    deleted_counter = 0

    @patch('taxi.clients.mds_avatars.MDSAvatarsClient.delete')
    async def _mds_avatars_delete_mock(*args, **kwargs):
        nonlocal deleted_counter
        deleted_counter += 1
        return 200

    @mockserver.handler(
        '/eats-restapp-authorizer/place-access/check', prefix=True,
    )
    def _mock_check(request):
        return mockserver.make_response(
            json=None
            if access_check_result == 200
            else {
                'code': 'some_code',
                'message': 'some message',
                'place_ids': [place_id],
            },
            status=access_check_result,
        )

    base_menu = await web_context.pg.master.fetchrow(
        'SELECT * FROM menu where place_id=$1;', str(place_id),
    )

    request_data = request_menu
    if delete_images:
        request_data['deleted_image_ids'] = delete_images
    response = await web_app_client.post(
        f'/restapp/v1/menu?place_id={place_id}',
        headers={'X-YaEda-PartnerId': partner_id},
        json=request_data,
    )

    updated_menu = await web_context.pg.master.fetchrow(
        'SELECT * FROM menu where place_id=$1;', str(place_id),
    )
    if base_menu and updated_menu:
        assert base_menu['menu'] == updated_menu['menu']
        assert updated_menu['updates'] == expected_db_updates
    assert response.status == expected_status
    if expected_status != 200:
        data = await response.json()
        assert data == expected_answer
    assert deleted_counter == expected_deleted_counter

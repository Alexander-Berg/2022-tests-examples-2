import pytest

from test_eats_integration_offline_orders import conftest


@pytest.mark.parametrize(
    'partner_id,place_id, expected_status, expected_answer, '
    'access_check_result',
    [
        pytest.param(
            '10',
            10,
            404,
            {'message': 'No menu found', 'code': 'no_menu'},
            200,
            id='no place',
        ),
        pytest.param(
            '10',
            1,
            400,
            {'message': 'Rest app request error', 'code': 'resp_app_error'},
            400,
            id='rest app error',
        ),
        pytest.param(
            '10',
            1,
            403,
            {'message': 'Access denied', 'code': 'no_access'},
            403,
            id='access denied',
        ),
        pytest.param(
            '1',
            1,
            200,
            conftest.FULL_MENU_UPDATES,
            200,
            id='full update menu',
        ),
        pytest.param(
            '1',
            2,
            200,
            conftest.PARTLY_UPDATED_MENU,
            200,
            id='part update menu',
        ),
        pytest.param(
            '1', 3, 200, conftest.BASE_MENU, 200, id='no update menu',
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
async def test_get_menu_restapp(
        web_app_client,
        mockserver,
        partner_id,
        place_id,
        expected_status,
        expected_answer,
        access_check_result,
):
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

    response = await web_app_client.get(
        f'/restapp/v1/menu?place_id={place_id}',
        headers={'X-YaEda-PartnerId': partner_id},
    )
    assert response.status == expected_status
    data = await response.json()
    assert data == expected_answer

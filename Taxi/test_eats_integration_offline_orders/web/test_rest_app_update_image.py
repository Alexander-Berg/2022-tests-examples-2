import pytest

IMAGE_ID = 'img_id'
GROUP_ID = 1


@pytest.mark.parametrize(
    'partner_id, place_id, loaded_file_check, expected_answer, '
    'expected_status, access_check_result, upload_group_id',
    [
        pytest.param(
            '10',
            3,
            True,
            {'message': 'Rest app request error', 'code': 'resp_app_error'},
            400,
            400,
            GROUP_ID,
            id='rest app error',
        ),
        pytest.param(
            '10',
            3,
            True,
            {'message': 'Access denied', 'code': 'no_access'},
            403,
            403,
            GROUP_ID,
            id='access denied',
        ),
        pytest.param(
            '10',
            10,
            True,
            {'message': 'No menu found', 'code': 'no_menu'},
            404,
            200,
            GROUP_ID,
            id='no place',
        ),
        pytest.param(
            '3',
            3,
            False,
            {'message': 'Specified file is not image', 'code': 'bad_request'},
            400,
            200,
            GROUP_ID,
            id='not image',
        ),
        pytest.param(
            '3',
            3,
            True,
            {'message': 'Unable to load image', 'code': 'internal_error'},
            400,
            200,
            None,
            id='not uploaded - no group_id',
        ),
        pytest.param(
            '3',
            3,
            True,
            {
                'image_id': f'{GROUP_ID}/{IMAGE_ID}',
                'url': (
                    f'$mockserver/mds_avatars/get-inplace/'
                    f'{GROUP_ID}/{IMAGE_ID}/orig'
                ),
            },
            200,
            200,
            GROUP_ID,
            id='success',
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
async def test_rest_app_update_image(
        web_app_client,
        patch,
        web_context,
        mockserver,
        partner_id,
        place_id,
        loaded_file_check,
        expected_answer,
        expected_status,
        access_check_result,
        upload_group_id,
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

    @patch(
        'eats_integration_offline_orders.components.avatars.'
        'check_content_is_image',
    )
    def _check_content_is_image(*args, **kwargs):
        return loaded_file_check

    @patch('taxi.clients.mds_avatars.MDSAvatarsClient.upload')
    async def _mds_avatars_upload_mock(*args, **kwargs):
        return upload_group_id, {}

    @patch(
        'eats_integration_offline_orders.components.avatars.'
        'generate_image_id',
    )
    def _generate_image_id(*args, **kwargs):
        return IMAGE_ID

    response = await web_app_client.post(
        f'/restapp/v1/image?place_id={place_id}&origin_id=origin_1',
        headers={'X-YaEda-PartnerId': partner_id},
        data=b'abc',
    )

    data = await response.json()
    assert data == expected_answer
    assert response.status == expected_status

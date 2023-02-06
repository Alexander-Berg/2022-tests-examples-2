import pytest

PHONE = 'phone'
PHONE_ID = 'phone_id'
PERSONAL_PHONE_ID = 'personal_id_123456789abcdef'
PHONE_TYPE = 'yandex'
TICKET = 'TAXIDATAREQUEST-123'
INTERNAL_SERVER_ERROR_RESPONSE = dict(
    code='INTERNAL_SERVER_ERROR', message='Internal server error',
)
CODE_TO_RESPONSE_MAP = {
    200: None,
    404: dict(
        code='user_not_found',
        message='User-api have not found phone from request',
    ),
    409: dict(
        code='conflict',
        message='User-api responsed with phone_id ' 'that caused bad request',
    ),
    500: INTERNAL_SERVER_ERROR_RESPONSE,
}


@pytest.mark.config(TVM_RULES=[{'src': 'admin-users-info', 'dst': 'personal'}])
@pytest.mark.parametrize(
    ['user_phone', 'personal_phone_id'],
    [
        pytest.param(PHONE, None, id='delete_by_phone'),
        pytest.param(PHONE, PERSONAL_PHONE_ID, id='delete_by_personal_id'),
    ],
)
@pytest.mark.parametrize(
    ['user_phones_code', 'user_phones_data'],
    [
        pytest.param(
            200,
            dict(
                phone_id=PHONE_ID,
                new_type=f'deleted:{PHONE_TYPE}:{TICKET}:uuid64',
            ),
            id='user_phones_200',
        ),
        pytest.param(
            404,
            dict(
                code='user_not_found',
                message='phone from request is not in db',
            ),
            id='user_phones_404',
        ),
        pytest.param(
            500, INTERNAL_SERVER_ERROR_RESPONSE, id='user_phones_500',
        ),
    ],
)
@pytest.mark.parametrize(
    ['users_code', 'users_data'],
    [
        pytest.param(200, dict(), id='users_200'),
        pytest.param(
            400,
            dict(code='bad_request', message='bad phone_id in request'),
            id='users_400',
        ),
        pytest.param(500, INTERNAL_SERVER_ERROR_RESPONSE, id='users_500'),
    ],
)
@pytest.mark.parametrize(
    ['safety_center_code', 'safety_center_data'],
    [
        pytest.param(200, dict(), id='safety_center_ok'),
        pytest.param(
            500, INTERNAL_SERVER_ERROR_RESPONSE, id='safety_center_500',
        ),
    ],
)
async def test_delete_user(
        web_app_client,
        mockserver,
        user_phones_code,
        user_phones_data,
        users_code,
        users_data,
        safety_center_code,
        safety_center_data,
        user_phone,
        personal_phone_id,
):
    if (
            safety_center_code == 200
            and user_phones_code == 200
            and users_code == 400
    ):
        expected_code = 409
    elif safety_center_code > 200:
        expected_code = safety_center_code
    elif user_phones_code > 200:
        expected_code = user_phones_code
    else:
        expected_code = users_code

    expected_response = CODE_TO_RESPONSE_MAP[expected_code]

    @mockserver.json_handler('/user-api/user_phones/remove')
    def _user_phones_remove_mock(request):
        assert request.json == dict(
            phone=user_phone, type=PHONE_TYPE, ticket=TICKET,
        )
        if user_phones_code == 500:
            raise mockserver.TimeoutError()
        return mockserver.make_response(
            status=user_phones_code, json=user_phones_data,
        )

    @mockserver.json_handler(f'/personal/v1/phones/retrieve')
    def _phone_retrieve(request):
        assert request.json == dict(id=personal_phone_id)
        return mockserver.make_response(
            status=200, json={'id': personal_phone_id, 'value': user_phone},
        )

    @mockserver.json_handler('/user-api/users/unauthorize-by-phone')
    def _users_unauthorize_by_phone_mock(request):
        assert request.json == dict(phone_id=PHONE_ID)
        if users_code == 500:
            raise mockserver.TimeoutError()
        return mockserver.make_response(status=users_code, json=users_data)

    @mockserver.json_handler('/safety-center/safety-center/v1/delete-user')
    def _safety_center_delete_user_mock(request):
        assert request.json == dict(phone=user_phone, phone_type=PHONE_TYPE)
        if safety_center_code == 500:
            raise mockserver.TimeoutError()
        return mockserver.make_response(
            status=safety_center_code, json=safety_center_data,
        )

    data = dict(phone_type=PHONE_TYPE, ticket=TICKET)
    if personal_phone_id is None:
        data.update(phone=user_phone)
    else:
        data.update(personal_phone_id=personal_phone_id)
    response = await web_app_client.post('/v1/delete-user', json=data)
    assert response.status == expected_code
    response_json = await response.json()
    if isinstance(response_json, dict) and 'details' in response_json:
        del response_json['details']
    assert response_json == expected_response

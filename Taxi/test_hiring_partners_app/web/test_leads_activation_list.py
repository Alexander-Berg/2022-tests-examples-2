async def test_v1_leads_activation_list__user_not_found(
        request_leads_activation_list, mock_personal,
):
    # arrange
    # act
    result = await request_leads_activation_list(
        request={}, user_login='non_existent_user', status_code=404,
    )

    # assert
    assert result == {
        'code': 'non_existent_user',
        'message': 'User non_existent_user does not exist',
    }


async def test_v1_leads_activation_list__user_is_not_activator(
        request_leads_activation_list, mock_personal,
):
    # arrange
    # act
    result = await request_leads_activation_list(
        request={}, user_login='yandexlogin_user_agent', status_code=403,
    )

    # assert
    assert result == {'code': 'invalid_role', 'message': 'Role is not allowed'}


async def test_v1_leads_activation_list__ok(
        request_leads_activation_list,
        mock_personal,
        mock_hiring_candidates_py3,
        load_json,
):
    # arrange
    # act
    result = await request_leads_activation_list(
        request={}, user_login='yandexlogin_user_activator', status_code=200,
    )

    # assert
    assert result == load_json('results.json')

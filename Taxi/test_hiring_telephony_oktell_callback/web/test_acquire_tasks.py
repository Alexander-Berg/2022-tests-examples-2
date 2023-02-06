async def test_acquire_task(
        load_json, taxi_hiring_telephony_oktell_callback_web, personal,
):
    # arrange
    request = load_json('requests.json')
    expected = load_json('responses.json')

    # act
    response = await taxi_hiring_telephony_oktell_callback_web.post(
        '/v2/tasks/oktell/acquire', json=request,
    )

    # assert
    assert response.status == 200
    data = await response.json()
    assert data == expected

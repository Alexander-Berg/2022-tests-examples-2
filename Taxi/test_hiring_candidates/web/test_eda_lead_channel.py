async def test_eda_channel_post(
        taxi_hiring_candidates_web,
        mock_statistics_retention,
        mock_configs3,
        load_json,
):
    # arrange
    data = load_json('request.json')
    configs3_mock = mock_configs3(response=load_json('config3.json'))
    mock_statistics_retention(retention=False)

    # act
    response = await taxi_hiring_candidates_web.post(
        '/v1/eda/channel', json=data,
    )

    # assert
    assert response.status == 200
    response_data = await response.json()
    assert response_data == {'channel': 'organic'}

    assert configs3_mock.times_called == 1
    call_request = configs3_mock.next_call()['request'].json
    assert call_request['args'] == load_json('config3_request_args.json')

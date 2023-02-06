def test_load_from_yt(taxi_chat, yt_client, load_json):
    query = (
        '* FROM [//home/taxi/unstable/services/chat/updates] '
        'WHERE chat_id = "chat_id" LIMIT 300'
    )
    yt_client.add_select_rows_response(query, 'yt-select-rows-response.json')

    response = taxi_chat.post(
        '1.0/chat/chat_id/history',
        {'include_metadata': True, 'include_participants': True},
    )
    assert response.status_code == 200
    data = response.json()
    expected = load_json('expected_response.json')
    assert data == expected

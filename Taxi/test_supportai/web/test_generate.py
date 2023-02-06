async def test_generate_texts(web_app_client, mock, mockserver):
    @mockserver.json_handler('/zeliboba/generative')
    async def _(_):
        return mockserver.make_response(
            status=200,
            json={
                'Responses': [
                    {'Response': 'Извинияю', 'Score': -0.1, 'NumTokens': 10},
                ],
            },
        )

    resp = await web_app_client.post(
        f'/v1/generate/texts?user_id=1&project_slug=ya_lavka',
        json={'text': 'Извини'},
    )
    assert resp.status == 200

    response_json = await resp.json()

    assert response_json['texts'][0] == 'Извинияю'

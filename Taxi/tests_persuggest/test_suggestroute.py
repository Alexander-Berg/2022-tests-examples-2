BASIC_REQUEST = {
    'user_identity': {
        'user_id': 'b300bda7d41b4bae8d58dfa93221ef16',
        'phone_id': '5714f45e98956f06baaae3d4',
    },
}


async def test_suggestroute(taxi_persuggest):
    response = await taxi_persuggest.post(
        'suggestroute', BASIC_REQUEST, headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 204

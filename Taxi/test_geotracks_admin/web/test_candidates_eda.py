from aiohttp import web


async def test_candidates_eda(web_app_client, mockserver):
    # pylint: disable=unused-variable
    @mockserver.json_handler('/eda-candidates/search')
    def search_candidates(request):
        return web.json_response(
            {
                'candidates': [
                    {'id': 'test_id_1', 'position': [54.675897, 56.326421]},
                    {'id': 'test_id_2', 'position': [54.675896, 56.326422]},
                ],
            },
        )

    response = await web_app_client.get(
        '/v1/candidates/eda',
        params={
            'latitude': '54.675897',
            'longitude': '56.326421',
            'max_distance': 10000,
            'limit': 100,
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {
        'candidates': [
            {
                'id': 'test_id_1',
                'position': {'latitude': 56.326421, 'longitude': 54.675897},
            },
            {
                'id': 'test_id_2',
                'position': {'latitude': 56.326422, 'longitude': 54.675896},
            },
        ],
    }

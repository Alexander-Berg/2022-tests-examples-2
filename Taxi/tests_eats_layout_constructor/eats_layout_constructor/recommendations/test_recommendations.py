import base64
import json


def encode_place_context(context: dict) -> str:
    out: str = json.dumps(context)
    return base64.standard_b64encode(out.encode('utf-8')).decode('utf-8')


async def test_endpoint_liveness(recommendations):
    response = await recommendations.make_request(
        headers={
            'x-device-id': 'testsuite',
            'X-Eats-Session': 'my-session',
            'X-Yandex-Uid': 'testsuite-uid',
        },
        body={
            'location': {'latitude': 55.750028, 'longitude': 37.534397},
            'last_visited_place': {
                'slug': 'place_1',
                'context': encode_place_context(
                    {
                        'place_id': 1,
                        'widget': {'id': '1', 'type': 'places_list'},
                    },
                ),
            },
            'nearest_places': [],
            'local_time': '2021-09-01T20:00:00+03:00',
        },
    )
    assert response.status_code == 200

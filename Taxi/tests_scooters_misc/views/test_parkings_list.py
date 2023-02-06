import operator


HANDLER_URL = '/v1/parkings/list'


async def test_handler(taxi_scooters_misc, load_json):
    res = await taxi_scooters_misc.get(HANDLER_URL)
    assert res.status_code == 200

    for resp, expected in zip(
            sorted(res.json()['parkings'], key=operator.itemgetter('id')),
            sorted(
                load_json('parkings_expected_response.json')['parkings'],
                key=operator.itemgetter('id'),
            ),
    ):
        assert resp == expected

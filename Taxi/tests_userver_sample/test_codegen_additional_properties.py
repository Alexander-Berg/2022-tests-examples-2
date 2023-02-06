import json


async def test_additional_properties_true(taxi_userver_sample):
    response = await taxi_userver_sample.post(
        'autogen/additional-properties-true',
        data=json.dumps(
            {'simple': {'x': 1, 'y': '2'}, 'with_extra': {'x': 1, 'y': '2'}},
        ),
    )
    assert response.status_code == 200
    assert response.json() == {
        'simple': {'x': 1, 'y': '2'},
        'with_extra': {'y': '2'},
        'x': 1,
    }

import json

import pytest


@pytest.mark.parametrize(
    ['get_surge_request', 'expected_status', 'expected_response'],
    [
        (
            {'point': {'lon': 36.1, 'lat': 58.1}},
            200,
            {'value': 0.6, 'features': [2.0]},
        ),
        (
            {'point': {'lon': 35.9, 'lat': 58.1}},
            404,
            {
                'code': 'ZONE_NOT_FOUND',
                'message': 'Zone not found for point [58.1, 35.9]',
            },
        ),
    ],
    ids=['happy_path', 'out_of_zone'],
)
@pytest.mark.config(
    SCOOTERS_ZONES=[
        {
            'geometry': [[36, 59], [36, 58], [37, 58]],
            'id': 'zone_id',
            'name': 'zone_name',
            'region_id': 'region_id',
        },
    ],
)
async def test_get_surge(
        taxi_scooters_surge,
        get_surge_request,
        expected_status,
        expected_response,
):
    await taxi_scooters_surge.invalidate_caches(
        cache_names=['surge-map-zoned-cache'],
    )
    response = await taxi_scooters_surge.post(
        'v1/get-surge', json=get_surge_request,
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response


@pytest.mark.now('2019-01-02T02:00:00+0000')
@pytest.mark.config(
    SCOOTERS_SURGE_READ_FROM_S3=True,
    SCOOTERS_ZONES=[
        {
            'geometry': [[36, 59], [36, 58], [37, 58]],
            'id': 'zone_id',
            'name': 'zone_name',
            'region_id': 'region_id',
        },
    ],
)
async def test_get_from_s3(taxi_scooters_surge, mockserver):
    surge_value = {'value': 1.6, 'features': [2.0]}
    requested_content_keys = set()
    requested_versions = set()

    @mockserver.handler('/mds-s3', prefix=True)
    def _mock_request_s3(request):
        if request.method == 'GET' or request.method == 'HEAD':
            content_key = request.path[len('/mds-s3/') :]
            requested_content_keys.add(content_key)
            if request.method == 'GET':
                requested_versions.add(request.query['versionId'])

            return mockserver.make_response(
                response=json.dumps({'zone_id': surge_value}),
                status=200,
                headers={
                    'X-Amz-Meta-Heatmapcompression': 'none',
                    'X-Amz-Meta-Heatmaptype': 'mapped_features',
                    'X-Amz-Meta-Created': '2019-01-02T01:00:00+0000',
                    'X-Amz-Meta-Expires': '2019-01-02T03:00:00+0000',
                    'X-Amz-Version-Id': 'current',
                },
            )

        return mockserver.make_response('Not found', 404)

    await taxi_scooters_surge.invalidate_caches(
        cache_names=['surge-map-zoned-cache'],
    )
    get_surge_request = {'point': {'lon': 36.1, 'lat': 58.1}}
    response = await taxi_scooters_surge.post(
        'v1/get-surge', json=get_surge_request,
    )
    assert response.status_code == 200
    assert response.json() == surge_value
    assert requested_content_keys == {'scooters_surge_zoned/default'}
    assert requested_versions == {'current'}

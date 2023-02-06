from aiohttp import web
import pytest


@pytest.mark.parametrize(
    ['params', 'status_code'],
    [
        (
            {
                # 'alias_id': '88b6352a14534ad0b46706b18240f360',
                'driver_id': '1',
                'park_id': '2',
                'timestamp': '1548315234',
                'max_acceleration': '150.5',
                'accident_speed': '1500.5',
                'latitide': '1500.51',
                'longitude': '1500.52',
                'bearing': '100.53',
            },
            web.HTTPBadRequest.status_code,
        ),
        (
            {
                'alias_id': '88b6352a14534ad0b46706b18240f360',
                # 'driver_id': '1',
                'park_id': '2',
                'timestamp': '1548315234',
                'max_acceleration': '150.5',
                'accident_speed': '1500.5',
                'latitide': '1500.51',
                'longitude': '1500.52',
                'bearing': '100.53',
            },
            web.HTTPBadRequest.status_code,
        ),
        (
            {
                'alias_id': '88b6352a14534ad0b46706b18240f360',
                'driver_id': '1',
                # 'park_id': '2',
                'timestamp': '1548315234',
                'max_acceleration': '150.5',
                'accident_speed': '1500.5',
                'latitide': '1500.51',
                'longitude': '1500.52',
                'bearing': '100.53',
            },
            web.HTTPBadRequest.status_code,
        ),
        (
            {
                'alias_id': '88b6352a14534ad0b46706b18240f360',
                'driver_id': '1',
                'park_id': '2',
                # 'timestamp': '1548315234',
                'max_acceleration': '150.5',
                'accident_speed': '1500.5',
                'latitide': '1500.51',
                'longitude': '1500.52',
                'bearing': '100.53',
            },
            web.HTTPBadRequest.status_code,
        ),
        (
            {
                'alias_id': '88b6352a14534ad0b46706b18240f360',
                'driver_id': '1',
                'park_id': '2',
                'timestamp': '1548315234',
                # 'max_acceleration': '150.5',
                'accident_speed': '1500.5',
                'latitide': '1500.51',
                'longitude': '1500.52',
                'bearing': '100.53',
            },
            web.HTTPBadRequest.status_code,
        ),
        (
            {
                'alias_id': '88b6352a14534ad0b46706b18240f360',
                'driver_id': '1',
                'park_id': '2',
                'timestamp': '1548315234',
                'max_acceleration': '150.5',
                # 'accident_speed': '1500.5',
                'latitide': '1500.51',
                'longitude': '1500.52',
                'bearing': '100.53',
            },
            web.HTTPBadRequest.status_code,
        ),
        (
            {
                'alias_id': '88b6352a14534ad0b46706b18240f360',
                'driver_id': '1',
                'park_id': '2',
                'timestamp': '1548315234',
                'max_acceleration': '150.5',
                'accident_speed': '1500.5',
                # 'latitide': '1500.51',
                'longitude': '1500.52',
                'bearing': '100.53',
            },
            web.HTTPBadRequest.status_code,
        ),
        (
            {
                'alias_id': '88b6352a14534ad0b46706b18240f360',
                'driver_id': '1',
                'park_id': '2',
                'timestamp': '1548315234',
                'max_acceleration': '150.5',
                'accident_speed': '1500.5',
                'latitide': '1500.51',
                # 'longitude': '1500.52',
                'bearing': '100.53',
            },
            web.HTTPBadRequest.status_code,
        ),
        (
            {
                'alias_id': '88b6352a14534ad0b46706b18240f360',
                'driver_id': '1',
                'park_id': '2',
                'timestamp': '1548315234',
                'max_acceleration': '150.5',
                'accident_speed': '1500.5',
                'latitide': '1500.51',
                'longitude': '1500.52',
                # 'bearing': '100.53',
            },
            web.HTTPBadRequest.status_code,
        ),
        (
            {
                'alias_id': '88b6352a14534ad0b46706b18240f360',
                'driver_id': '1',
                'park_id': '2',
                'timestamp': '1548315234',
                'max_acceleration': '150.5',
                'accident_speed': '1500.5',
                'latitide': '1500.51',
                'longitude': '1500.52',
                'bearing': '100.53',
            },
            web.HTTPOk.status_code,
        ),
        (
            {
                'alias_id': '88b6352a14534ad0b46706b18240f360',
                'driver_id': '1',
                'park_id': '2',
                'timestamp': '1548315234',
                'max_acceleration': '150.5',
                'accident_speed': '1500.5',
                'latitide': '1500.51',
                'longitude': '1500.52',
                'bearing': '100.53',
                'probability': '50.35',
            },
            web.HTTPOk.status_code,
        ),
    ],
)
async def test_road_accident(support_info_client, patch, params, status_code):
    @patch('taxi.stq.client.put')
    async def _put(
            queue, eta=None, task_id=None, args=None, kwargs=None, loop=None,
    ):
        pass

    response = await support_info_client.post(
        '/v1/road_accident/create',
        json=params,
        headers={'YaTaxi-Api-Key': 'api-key'},
    )
    assert response.status == status_code

    if response.status == web.HTTPOk.status_code:
        stq_args = _put.calls[0]
        assert stq_args['queue'] == 'support_info_road_accident_ticket'
        assert stq_args['args'] == (params,)
        assert 'log_extra' in stq_args['kwargs']

import pytest


async def test_log_types_v1(web_app_client):
    response = await web_app_client.get('/log_types/')
    assert response.status == 200
    assert await response.json() == {
        'log_types': ['buffer_dispatch', 'driver_dispatcher', 'tracks'],
    }


@pytest.mark.config(
    DISPATCH_LOGS_ADMIN={
        'log_sources': {
            'buffer_dispatch': {'path_prefix': '', 'path': ''},
            'driver_dispatcher': {'path': ''},
        },
    },
    DISPATCH_LOGS_QUERY_SETTINGS={
        '__default__': {
            'order_id_fields': ['order_id'],
            'draw_id_fields': ['draw_id'],
            'timestamp': {'field_type': 'integer', 'field_name': 'timestamp'},
        },
        'driver_dispatcher': {
            'order_id_fields': ['order_id'],
            'draw_id_fields': ['draw_id'],
            'driver_id_fields': ['dbid', 'clid', 'uuid', 'udid'],
            'any_filter_fields': [],
            'timestamp': {'field_type': 'integer', 'field_name': 'timestamp'},
        },
    },
)
async def test_log_types(web_app_client, taxi_config):
    response = await web_app_client.get('/v2/log_types/')
    assert response.status == 200
    data = await response.json()
    for log_type in data['log_types'].keys():
        data['log_types'][log_type]['filters'].sort()

    assert data == {
        'log_types': {
            'buffer_dispatch': {'filters': ['draw_id', 'order_id']},
            'driver_dispatcher': {
                'filters': ['draw_id', 'driver_id', 'order_id'],
            },
        },
    }

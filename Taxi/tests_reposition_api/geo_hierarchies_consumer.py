import json


def build_raw_event(dbid, uuid, geo_hierarchy, updated_at):
    return json.dumps(
        {
            'park_id': dbid,
            'driver_id': uuid,
            'geo_hierarchy': geo_hierarchy,
            'updated_at': updated_at,
        },
    )


async def post_event(taxi_reposition_api, raw_event, cookie='cookie'):
    response = await taxi_reposition_api.post(
        'tests/logbroker/messages',
        data=json.dumps(
            {
                'consumer': 'reposition-api',
                'data': raw_event,
                'topic': (
                    '/taxi/contractor-events-producer/testing/'
                    'contractor-geo-hierarchies'
                ),
                'cookie': cookie,
            },
        ),
    )

    assert response.status_code == 200

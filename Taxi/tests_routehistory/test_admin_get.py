import pytest

from . import utils


@pytest.mark.parametrize(
    'request_obj, expected_response_file',
    [
        (
            {
                'phone_id': '123456789abcdef123456789',
                'order_id': '11111111000000000000000000000007',
            },
            'response_1.json',
        ),
        (
            {
                'phone_id': '111111111111111111111111',
                'order_id': '11111111000000000000000000000007',
            },
            None,
        ),
        (
            {
                'phone_id': '123456789abcdef123456789',
                'order_id': '22222222222222222222222222222222',
            },
            None,
        ),
        (
            {
                'phone_id': '1dcf5804abae14bb0d31d02d',
                'order_id': '11111111000000000000000000000003',
            },
            'response_2.json',
        ),
    ],
)
async def test_admin_get(
        taxi_routehistory,
        pgsql,
        load_json,
        request_obj,
        expected_response_file,
        yamaps,
):
    utils.fill_db(pgsql['routehistory'].cursor(), load_json('db.json'))
    utils.fill_db(pgsql['routehistory_ph'].cursor(), load_json('db_ph.json'))

    @yamaps.set_fmt_geo_objects_callback
    def _get_geo_objects(request):
        geo_objects = load_json('yamaps_geo_objects.json')
        if 'uri' in request.args:
            for addr in geo_objects:
                if addr['uri'] == request.args['uri']:
                    return [addr]
        return []

    response = await taxi_routehistory.post(
        'routehistory/admin/get', request_obj, headers={},
    )
    expected_response = (
        load_json(expected_response_file) if expected_response_file else {}
    )
    assert response.status_code == 200
    assert response.json() == expected_response

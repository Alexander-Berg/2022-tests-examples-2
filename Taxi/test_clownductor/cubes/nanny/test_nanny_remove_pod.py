from aiohttp import web

from clownductor.internal.tasks import cubes


async def test_nanny_remove_pod_bad_request(
        mockserver,
        nanny_mockserver,
        nanny_yp_mockserver,
        staff_mockserver,
        web_context,
        task_data,
):
    nanny_yp_mockserver()
    staff_mockserver()

    nanny_yp_mockserver()

    @mockserver.json_handler('/client-nanny-yp/api/yplite/pod-sets/RemovePod/')
    def yp_handler(_):
        return web.Response(status=400, headers=None, text='Bad request')

    cube = cubes.CUBES['NannyRemovePods'](
        web_context,
        task_data('NannyRemovePods'),
        {'pod_ids': ['jpa75d4ifcp724r2', 'znuucofbn3ix2ag2'], 'region': 'man'},
        [],
        None,
    )

    await cube.update()
    assert yp_handler.times_called == 1
    assert cube.in_progress

import pytest

CUBE_NAME = 'NannyGetRuntimeAttrsInfo'


@pytest.mark.pgsql('clownductor', files=['init_data.sql'])
async def test_cube_handler_cancel(
        load_json,
        mockserver,
        nanny_mockserver,
        nanny_yp_mockserver,
        call_cube_handle,
        web_context,
):
    nanny_yp_mockserver()

    @mockserver.json_handler(
        '/client-nanny/v2/services/' 'test_404_service_sas/runtime_attrs/',
    )
    def _request(_):
        return mockserver.make_response(status=404, json={})

    await call_cube_handle(CUBE_NAME, load_json(f'cube_data_cancel.json'))
    job = await web_context.service_manager.jobs.get_by_id(1)
    assert job['status'] == 'canceled'

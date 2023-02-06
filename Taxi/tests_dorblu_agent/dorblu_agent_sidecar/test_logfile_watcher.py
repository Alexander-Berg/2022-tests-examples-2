import pytest


@pytest.mark.now('2017-09-09T00:00:00+0300')
async def test_simple(
        default_log_path,
        taxi_dorblu_agent_sidecar,
        testpoint,
        start_dorblu_agent,
        fill_default_access_log,
):
    await start_dorblu_agent()

    fill_default_access_log('simple_nginx_access.log')

    @testpoint('logfile_positions')
    def logfile_positions_tp(data):
        assert data == {
            str(default_log_path): [
                {'time': '2017-09-08T21:00:00+0000', 'position': 4},
            ],
        }

    await taxi_dorblu_agent_sidecar.run_periodic_task('logfile-watcher')

    assert logfile_positions_tp.times_called == 1

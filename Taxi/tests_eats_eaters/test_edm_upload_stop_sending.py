import pytest


import tests_eats_eaters.edm_utils as edm_utils


@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(0),
)
async def test_edm_task_stop_sending(
        taxi_eats_eaters, taxi_eats_eaters_monitor, mockserver, pgsql,
):
    await taxi_eats_eaters.tests_control(reset_metrics=True)

    psql_cursor = pgsql['eats_eaters'].cursor()
    edm_utils.initialize_meta_table(psql_cursor)

    @mockserver.json_handler('/eats-data-mappings/v1/pairs')
    def mock_edm_pairs(request):
        assert False

    psql_cursor = pgsql['eats_eaters'].cursor()
    edm_utils.insert_eater(psql_cursor, 1, '2020-06-15T13:00:00+00:00')

    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 0

    assert {
        'sent-data': 0,
        'interpolated-chunk-size': 0.0,
        'chunk-size-limit': 0,
        'data-to-send-in-minute-limit': 0.0,
        'sync-delay-real-sec': 0,
        'sync-delay-offset-sec': 120,
        'run-period-ms': 500,
        'real-run-period-ms': 0,
        'step-time-ms': 0,
    } == await edm_utils.get_metric(taxi_eats_eaters_monitor)

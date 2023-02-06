import pytest


import tests_eats_eaters.edm_utils as edm_utils


@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(),
)
async def test_edm_task_simple_test(taxi_eats_eaters, mockserver, pgsql):
    psql_cursor = pgsql['eats_eaters'].cursor()
    edm_utils.initialize_meta_table(psql_cursor)

    @mockserver.json_handler('/eats-data-mappings/v1/pairs')
    def mock_edm_pairs(request):
        assert {'pairs': edm_utils.user_expected(1)} == request.json
        return mockserver.make_response(status=204)

    psql_cursor = pgsql['eats_eaters'].cursor()
    edm_utils.insert_eater(psql_cursor, 1, '2020-06-15T13:00:00+00:00')

    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 1


@pytest.mark.config(
    EATS_DATA_MAPPINGS_UPLOAD_PARAMS=edm_utils.get_default_config(),
)
async def test_edm_task_two_rows(taxi_eats_eaters, mockserver, pgsql):
    psql_cursor = pgsql['eats_eaters'].cursor()
    edm_utils.initialize_meta_table(psql_cursor)

    @mockserver.json_handler('/eats-data-mappings/v1/pairs')
    def mock_edm_pairs(request):
        assert {'pairs': edm_utils.user_expected([1, 2])} == request.json
        return mockserver.make_response(status=204)

    psql_cursor = pgsql['eats_eaters'].cursor()
    edm_utils.insert_eater(psql_cursor, 1, '2020-06-15T13:00:00+00:00')
    edm_utils.insert_eater(psql_cursor, 2, '2020-06-15T13:01:00+00:00')

    await edm_utils.run_task(taxi_eats_eaters)
    assert mock_edm_pairs.times_called == 1

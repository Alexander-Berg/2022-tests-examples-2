import pytest

TASK_NAME = 'eats-performer-statistics-update-retention-status-periodic'


@pytest.fixture(name='mock_yql')
def _mock_yql(mockserver, load):
    class Context:
        _results_data = None
        _results_call_number = 0

        @property
        def results_data(self):
            return self._results_data

        def set_results_data(self, results_data):
            self._results_data = results_data

    context = Context()

    @mockserver.json_handler('/yql/api/v2/operations')
    def _new_operation(request):
        return {'id': 'abcde12345'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)', regex=True,
    )
    def _operation_status(request, operation_id):
        return {'id': operation_id, 'status': 'COMPLETED'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/results', regex=True,
    )
    def _operation_status_results(request, operation_id):
        return {'id': operation_id, 'status': 'COMPLETED'}

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/share_id', regex=True,
    )
    def _operation_url(request, operation_id):
        return 'this_is_share_url'

    @mockserver.json_handler(
        r'/yql/api/v2/operations/(?P<operation_id>\w+)/results_data',
        regex=True,
    )
    def _operation_results_data(request, operation_id):
        return mockserver.make_response(
            load(
                context.results_data[
                    'offset_{}_limit_{}'.format(
                        request.args['offset'], request.args['limit'],
                    )
                ],
            ),
            content_type='application/json',
            status=200,
        )

    return context


@pytest.mark.parametrize(
    ['phone_pd_id', 'retention'],
    [
        ('44444', False),  # there is no phone_pd_id
        ('22222', True),  # phone_pd_id exist, but not latest version
        ('33333', True),  # phone_pd_id exist in latest version
        ('55555', True),
    ],
)
@pytest.mark.pgsql('eats_performer_statistics', files=['fill_data.sql'])
async def test_retention_retrieve(
        taxi_eats_performer_statistics, phone_pd_id, retention,
):

    response = await taxi_eats_performer_statistics.post(
        '/internal/eats-performer-statistics/v1/eda/retention/retrieve',
        json={'phone_pd_id': phone_pd_id},
    )

    assert response.status_code == 200
    assert response.json() == {'retention': retention}


def sql_get_courier_phone_numbers(pgsql):
    cursor = pgsql['eats_performer_statistics'].cursor()
    cursor.execute(
        """
        SELECT *
        FROM eats_performer_statistics.retention
        """,
    )
    return list(cursor)


@pytest.mark.yt(
    dyn_table_data=[
        'yt_eda_dm_order.yaml',
        'yt_dm_lavka_order.yaml',
        'yt_courier_personal_data_identifier.yaml',
    ],
    static_table_data=['yt_retention_phone_pd_id_temp.yaml'],
)
@pytest.mark.now('2022-06-28T20:30:00+00:00')
@pytest.mark.config(
    EATS_PERFORMER_STATISTICS_YQL_QUERY_READER_SETTINGS={
        'status_retry_interval_ms': 1,
        'status_total_wait_ms': 1000,
        'read_chunk_size': 500,
        'tmp_directory_retention': (
            '//tmp/eats_performer_statistics/testing/retention/phone_pd_ids'
        ),
    },
)
async def test_update_retention_periodic(
        taxi_eats_performer_statistics, pgsql, mockserver, yt_apply, mock_yql,
):

    await taxi_eats_performer_statistics.run_periodic_task(TASK_NAME)

    result = sql_get_courier_phone_numbers(pgsql)

    assert result == [('phonepdidtest', 1), ('phonepdidtest2', 1)]

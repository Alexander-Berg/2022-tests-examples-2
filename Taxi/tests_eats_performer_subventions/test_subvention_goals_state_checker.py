import pytest


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


async def get_actual_orders_count(cursor, performer_ids):
    query_ids = [
        '\'{0}\''.format(performer_id) for performer_id in performer_ids
    ]
    cursor.execute(
        """
SELECT
    psog.performer_id, psog.actual_orders_count AS order_count, psog.status
FROM eats_performer_subventions.performer_subvention_order_goals psog
WHERE psog.performer_id IN ({0})
        """.format(
            ', '.join(query_ids),
        ),
    )
    goals_statuses = cursor.fetchall()

    return {goal['performer_id']: goal for goal in goals_statuses}


@pytest.mark.pgsql(
    'eats_performer_subventions', files=['subvention_goals_state_checker.sql'],
)
@pytest.mark.config(
    EATS_PERFORMER_SUBVENTIONS_SUBVENTION_GOALS_STATE_CHECKER_SETTINGS={
        'period_sec': 600,
        'is_enabled': True,
        'db_read_chunk_size': 2,
        'yt_orders_count_table': (
            '//tmp/eats-performer-subventions/dxgy/orders-count'
        ),
        'close_goal_delay_in_hours': 24,
        'close_daily_goal_delay_in_hours': 48,
        'interval_between_goal_checks_in_secs': 86400,
    },
    EATS_PERFORMER_SUBVENTIONS_YQL_QUERY_READER_SETTINGS={
        'status_retry_interval_ms': 1,
        'status_total_wait_ms': 1000,
        'read_chunk_size': 500,
    },
)
@pytest.mark.yt(static_table_data=['yt_orders_data.yaml'])
@pytest.mark.parametrize(
    'performer_goal_states',
    [
        pytest.param(
            {
                '1': {'order_count': 0, 'status': 'in_progress'},
                '2': {'order_count': 0, 'status': 'finished'},
                '3': {'order_count': 0, 'status': 'failed'},
                '4': {'order_count': 0, 'status': 'in_progress'},
                '5': {'order_count': 0, 'status': 'in_progress'},
                '6': {'order_count': 0, 'status': 'in_progress'},
                '7': {'order_count': 0, 'status': 'in_progress'},
            },
            marks=[pytest.mark.now('2022-01-01T15:34:00+03:00')],
            id='no goals to check',
        ),
        pytest.param(
            {
                '1': {'order_count': 0, 'status': 'in_progress'},
                '2': {'order_count': 0, 'status': 'finished'},
                '3': {'order_count': 0, 'status': 'failed'},
                '4': {'order_count': 0, 'status': 'in_progress'},
                '5': {'order_count': 0, 'status': 'in_progress'},
                '6': {'order_count': 0, 'status': 'in_progress'},
                '7': {'order_count': 0, 'status': 'in_progress'},
            },
            marks=[pytest.mark.now('2022-01-31T20:00:00+00:00')],
            id='no goals to check, the day before',
        ),
        pytest.param(
            {
                '1': {'order_count': 16, 'status': 'in_progress'},
                '2': {'order_count': 0, 'status': 'finished'},
                '3': {'order_count': 0, 'status': 'failed'},
                '4': {'order_count': 0, 'status': 'in_progress'},
                '5': {'order_count': 0, 'status': 'in_progress'},
                '6': {'order_count': 0, 'status': 'in_progress'},
                '7': {'order_count': 0, 'status': 'in_progress'},
            },
            marks=[
                pytest.mark.now('2022-02-01T20:00:00+00:00'),
                pytest.mark.yt(
                    static_table_data=['yt_orders_data_first_day.yaml'],
                ),
            ],
            id='one goal, first day of period',
        ),
        pytest.param(
            {
                '1': {'order_count': 37, 'status': 'finished'},
                '2': {'order_count': 0, 'status': 'finished'},
                '3': {'order_count': 0, 'status': 'failed'},
                '4': {'order_count': 12, 'status': 'in_progress'},
                '5': {'order_count': 0, 'status': 'in_progress'},
                '6': {'order_count': 0, 'status': 'in_progress'},
                '7': {'order_count': 21, 'status': 'finished'},
            },
            marks=[
                pytest.mark.now('2022-02-05T00:00:00+00:00'),
                pytest.mark.yt(
                    static_table_data=['yt_orders_data_finished.yaml'],
                ),
            ],
            id='goal is finished, other are going, one was already checked',
        ),
        pytest.param(
            {
                '1': {'order_count': 37, 'status': 'finished'},
                '2': {'order_count': 0, 'status': 'finished'},
                '3': {'order_count': 0, 'status': 'failed'},
                '4': {'order_count': 22, 'status': 'in_progress'},
                '5': {'order_count': 10, 'status': 'failed'},
                '6': {'order_count': 2, 'status': 'in_progress'},
                '7': {'order_count': 21, 'status': 'finished'},
            },
            marks=[pytest.mark.now('2022-02-10T00:00:00+00:00')],
            id='time is gone',
        ),
        pytest.param(
            {
                '1': {'order_count': 37, 'status': 'finished'},
                '2': {'order_count': 0, 'status': 'finished'},
                '3': {'order_count': 0, 'status': 'failed'},
                '4': {'order_count': 22, 'status': 'failed'},
                '5': {'order_count': 10, 'status': 'failed'},
                '6': {'order_count': 2, 'status': 'finished'},
                '7': {'order_count': 21, 'status': 'finished'},
            },
            id='time is gone (chunks)',
            marks=[
                pytest.mark.now('2022-02-12T00:00:00+00:00'),
                pytest.mark.config(
                    EATS_PERFORMER_SUBVENTIONS_SUBVENTION_GOALS_STATE_CHECKER_SETTINGS={  # noqa: E501
                        'period_sec': 600,
                        'is_enabled': True,
                        'db_read_chunk_size': 20,
                        'yt_orders_count_table': '//tmp/eats-performer-subventions/dxgy/orders-count',  # noqa: E501
                        'close_goal_delay_in_hours': 24,
                        'interval_between_goal_checks_in_secs': 86400,
                    },
                    EATS_PERFORMER_SUBVENTIONS_YQL_QUERY_READER_SETTINGS={
                        'status_retry_interval_ms': 1,
                        'status_total_wait_ms': 1000,
                        'read_chunk_size': 10,
                    },
                ),
            ],
        ),
    ],
)
async def test_subvention_goals_state_checker(
        taxi_eats_performer_subventions,
        pgsql,
        mock_yql,
        performer_goal_states,
):
    cursor = pgsql['eats_performer_subventions'].dict_cursor()
    performer_ids = [k for k, v in performer_goal_states.items()]

    actual_order_counts = await get_actual_orders_count(cursor, performer_ids)

    for performer_id in performer_ids:
        assert actual_order_counts[performer_id]['order_count'] == 0

    await taxi_eats_performer_subventions.run_periodic_task(
        'subvention-goals-state-checker-periodic',
    )

    actual_order_counts = await get_actual_orders_count(cursor, performer_ids)

    for performer_id in performer_ids:
        assert (
            actual_order_counts[performer_id]['order_count']
            == performer_goal_states[performer_id]['order_count']
        )
        assert (
            actual_order_counts[performer_id]['status']
            == performer_goal_states[performer_id]['status']
        )

import pytest

HANDLER_INTERSECTIONS = '/eats-shifts/server-api/shift-data/intersections'

METRICS_RESET = 'metrics-collector-reset-statistics'


@pytest.mark.now('2019-04-10T21:00:00+0000')
@pytest.mark.experiments3(filename='experiments3_experiments_pipeline.json')
@pytest.mark.experiments3(
    name='eats_pauouts_courier_demand_pipeline_arguments',
    consumers=['eats-logistics-performer-payouts/courier-demand-calculator'],
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    default_value={
        'pipeline_name': 'courier_demand_pclinear',
        'coeff_basic': 1.1,
        'coeff_low_density': 1.4,
        'coeff_ll_min': 50,
        'coeff_ll_max': 75,
        'coeff_surge_slope': 14.0,
    },
    clauses=[],
)
@pytest.mark.pgsql(
    'eats_logistics_performer_payouts',
    files=['eats_logistics_performer_payouts/insert_subject_for_stq_calc.sql'],
)
async def test_stq_calculation(
        taxi_eats_logistics_performer_payouts,
        taxi_eats_logistics_performer_payouts_monitor,
        mockserver,
        testpoint,
        stq_runner,
):
    @mockserver.json_handler(HANDLER_INTERSECTIONS)
    def mock_shift_intersections(request):
        req_shift_id = request.query['shift_id']
        assert req_shift_id is not None
        return {'data': {'shifts': []}}

    @testpoint('test_missed_time')
    def check_missed_times(missed_times_data):
        assert missed_times_data == 0.75

    @testpoint('check_pipeline_input')
    def check_pipeline_input(data):
        def sorted_data(values):
            values['request']['coefficients_values'] = dict(
                values['request']['coefficients_values'],
            )
            values['request']['subject']['factors'] = dict(
                values['request']['subject']['factors'],
            )
            for linked_subject in values['request']['subject'][
                    'linked_subjects'
            ]:
                linked_subject['factors'] = dict(linked_subject['factors'])
                linked_subject = dict(linked_subject)
            values['request']['subject'] = dict(values['request']['subject'])
            values['request'] = dict(values['request'])
            return values

        assert sorted_data(data) == sorted_data(expected_pipeline_input)

    # Flag indicating whether to include the current period in metrics
    @testpoint('include_current_period_testpoint')
    def include_current_period_tp(data):
        return True

    expected_pipeline_input = {
        'request': {
            'coefficients_values': {
                'fine_thresh_early': 10.0,
                'fine_thresh_late': 10.0,
                'max_missed_time': 10.0,
                'per_hour_guarantee': 300.0,
            },
            'settings': {
                'coeff_basic': 1.1,
                'coeff_low_density': 1.4,
                'is_low_density_lite': False,
                'll_max': 75,
                'll_min': 50,
                'surge_slope': 14.0,
            },
            'subject': {
                'external_id': '1',
                'factors': {
                    'actual_end_at': {
                        'id': 1,
                        'value': '2019-04-10T21:00:13+00:00',
                    },
                    'actual_start_at': {
                        'id': 3,
                        'value': '2019-04-10T12:00:45+00:00',
                    },
                    'eats_region_id': {'id': 7, 'value': '1'},
                    'fraud_on_start': {'id': 5, 'value': 0},
                    'is_newbie': {'id': 6, 'value': 0},
                    'missed_time': {'id': 0, 'value': '0.75'},
                    'planned_end_at': {
                        'id': 2,
                        'value': '2019-04-10T21:00:00+00:00',
                    },
                    'planned_start_at': {
                        'id': 4,
                        'value': '2019-04-10T12:00:00+00:00',
                    },
                    'post': {'id': 8, 'value': 'picker'},
                    'status': {'id': 18, 'value': 'closed'},
                    'travel_type': {'id': 9, 'value': 'pedestrian'},
                    'type': {'id': 10, 'value': 'planned'},
                },
                'level': 0,
                'linked_subjects': [
                    {
                        'external_id': '1',
                        'factors': {
                            'country_id': {'id': 12, 'value': '35'},
                            'eats_region_id': {'id': 13, 'value': '1'},
                            'pool': {'id': 14, 'value': 'shop'},
                            'transport_type': {
                                'id': 15,
                                'value': 'pedestrian',
                            },
                            'username': {
                                'id': 16,
                                'value': 'Суперсборщик Ростислав',
                            },
                            'recently_hours_worked': {'id': 20, 'value': '10'},
                            'recently_km_passed': {'id': 19, 'value': '10.03'},
                            'recently_orders_completed': {
                                'id': 21,
                                'value': 5,
                            },
                        },
                        'level': 1,
                        'linked_subjects': [],
                        'performer_id': 1,
                        'time_point_at': None,
                        'type': 'performer',
                    },
                ],
                'performer_id': 0,
                'time_point_at': None,
                'type': 'shift',
            },
        },
    }

    await taxi_eats_logistics_performer_payouts.run_task(METRICS_RESET)
    await stq_runner.calculate_offer_from_db.call(
        task_id='test_stq_task',
        kwargs={'external_id': '1', 'subject_type': 'shift'},
    )

    assert check_missed_times.times_called == 1
    assert mock_shift_intersections.times_called == 1
    assert check_pipeline_input.times_called == 1
    metrics = await taxi_eats_logistics_performer_payouts_monitor.get_metric(
        'metrics-collector',
    )
    assert include_current_period_tp.times_called == 1
    assert metrics == {
        'number_of_shifts': 1,
        'number_of_orders': 0,
        'hours_worked': 8.99,
        'money_on_hands': 2700.0,
        'orders_part': 0,
    }

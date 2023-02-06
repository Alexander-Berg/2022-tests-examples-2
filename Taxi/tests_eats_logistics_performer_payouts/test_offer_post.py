import pytest


@pytest.mark.config(
    EATS_LOGISTICS_PERFORMER_PAYOUTS_VERIFIED_UNITS_V2={
        'verified_courier_type': ['picker'],
        'verified_courier_id': ['1'],
        'verified_region': ['1'],
        'verified_calculation_schemas': [],
    },
)
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
    files=[
        'eats_logistics_performer_payouts/'
        'insert_coefficients_for_offer_test.sql',
    ],
)
async def test_offer(taxi_eats_logistics_performer_payouts, pgsql, testpoint):
    @testpoint('check_subject_context')
    def check_subject_context(data):
        assert dict(expected_subject_context) == dict(data)

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
                for linked_linked_subject in linked_subject['linked_subjects']:
                    linked_linked_subject['factors'] = dict(
                        linked_linked_subject['factors'],
                    )
                    linked_linked_subject = dict(linked_linked_subject)
            values['request']['subject'] = dict(values['request']['subject'])
            values['request'] = dict(values['request'])
            return values

        assert sorted_data(expected_pipeline_input) == sorted_data(data)

    def sorted_response(data):
        data['fine_explanations'] = sorted(data['fine_explanations'])
        data['guarantee_loss_reasons'] = sorted(data['guarantee_loss_reasons'])
        return dict(data)

    request = {
        'id': {'id': '1', 'type': 'shift'},
        'subjects': [
            {
                'id': {'id': '1', 'type': 'shift'},
                'factors': [
                    {'name': 'eats_region_id', 'type': 'string', 'value': '1'},
                    {
                        'name': 'planned_start_at',
                        'type': 'datetime',
                        'value': '2019-04-10T12:00:00+00:00',
                    },
                    {
                        'name': 'actual_start_at',
                        'type': 'datetime',
                        'value': '2019-04-10T12:27:45+00:00',
                    },
                    {
                        'name': 'planned_end_at',
                        'type': 'datetime',
                        'value': '2019-04-10T21:00:00+00:00',
                    },
                    {
                        'name': 'actual_end_at',
                        'type': 'datetime',
                        'value': '2019-04-10T20:28:13+00:00',
                    },
                    {'name': 'fraud_on_start', 'type': 'int', 'value': 1},
                    {'name': 'is_newbie', 'type': 'int', 'value': 0},
                    {
                        'name': 'travel_type',
                        'type': 'string',
                        'value': 'pedestrian',
                    },
                    {'name': 'post', 'type': 'string', 'value': 'picker'},
                    {'name': 'type', 'type': 'string', 'value': 'planned'},
                    {
                        'name': 'missed_time',
                        'type': 'decimal',
                        'value': '60.0',
                    },
                ],
                'relations': [{'id': '1', 'type': 'performer'}],
            },
            {
                'id': {'id': '1', 'type': 'performer'},
                'factors': [
                    {'name': 'country_id', 'type': 'string', 'value': '35'},
                    {'name': 'eats_region_id', 'type': 'string', 'value': '1'},
                    {'name': 'pool', 'type': 'string', 'value': 'shop'},
                    {
                        'name': 'transport_type',
                        'type': 'string',
                        'value': 'pedestrian',
                    },
                    {
                        'name': 'salary_adjustments',
                        'type': 'decimal',
                        'value': '0.00',
                    },
                    {
                        'name': 'username',
                        'type': 'string',
                        'value': 'Суперсборщик Ростислав',
                    },
                    {
                        'name': 'timezone',
                        'type': 'string',
                        'value': 'Europe/Moscow',
                    },
                ],
                'relations': [{'id': '1', 'type': 'courier_service'}],
            },
            {
                'id': {'id': '1', 'type': 'courier_service'},
                'factors': [
                    {'name': 'name', 'type': 'string', 'value': 'ООО Тест'},
                ],
            },
        ],
    }
    expected_subject_context = {
        'country_id': '35',
        'region_id': '1',
        'pool': 'shop',
        'courier_type': 'picker',
    }
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
                        'id': 0,
                        'value': '2019-04-10T20:28:13+00:00',
                    },
                    'actual_start_at': {
                        'id': 0,
                        'value': '2019-04-10T12:27:45+00:00',
                    },
                    'eats_region_id': {'id': 0, 'value': '1'},
                    'fraud_on_start': {'id': 0, 'value': 1},
                    'is_newbie': {'id': 0, 'value': 0},
                    'planned_end_at': {
                        'id': 0,
                        'value': '2019-04-10T21:00:00+00:00',
                    },
                    'planned_start_at': {
                        'id': 0,
                        'value': '2019-04-10T12:00:00+00:00',
                    },
                    'post': {'id': 0, 'value': 'picker'},
                    'travel_type': {'id': 0, 'value': 'pedestrian'},
                    'type': {'id': 0, 'value': 'planned'},
                    'missed_time': {'id': 0, 'value': '60'},
                },
                'level': 0,
                'linked_subjects': [
                    {
                        'external_id': '1',
                        'factors': {
                            'country_id': {'id': 0, 'value': '35'},
                            'eats_region_id': {'id': 0, 'value': '1'},
                            'pool': {'id': 0, 'value': 'shop'},
                            'salary_adjustments': {'id': 0, 'value': '0'},
                            'transport_type': {'id': 0, 'value': 'pedestrian'},
                            'username': {
                                'id': 0,
                                'value': 'Суперсборщик Ростислав',
                            },
                            'timezone': {'id': 0, 'value': 'Europe/Moscow'},
                        },
                        'level': 1,
                        'linked_subjects': [
                            {
                                'external_id': '1',
                                'factors': {
                                    'name': {'id': 0, 'value': 'ООО Тест'},
                                },
                                'level': 2,
                                'linked_subjects': [],
                                'performer_id': 0,
                                'time_point_at': None,
                                'type': 'courier_service',
                            },
                        ],
                        'performer_id': 0,
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
    expected_response = {
        'success': True,
        'actual_end_at': '2019-04-10T23:28:13+03:00',
        'actual_end_at_local_tz': '2019-04-10T23:28:13+03:00',
        'actual_hours': 8.01,
        'actual_start_at': '2019-04-10T15:27:45+03:00',
        'actual_start_at_local_tz': '2019-04-10T15:27:45+03:00',
        'calculation_schema': '',
        'cancelled_dropoff': 0.0,
        'cancelled_pickup': 0,
        'count_no_show_shifts': 0,
        'courier_id': '1',
        'courier_name': 'Суперсборщик Ростислав',
        'courier_service_commission': 0.0,
        'courier_service_id': 0.0,
        'courier_service_name': '',
        'courier_type': 'pedestrian',
        'country_id': '',
        'date': '2019-04-10',
        'delivery_fee': 0.0,
        'distance_to_customer': 0.0,
        'distance_to_place': 0.0,
        'dropoff_part': 0.0,
        'early_end_min': 31.78,
        'fine_amount': 300.0,
        'max_missed_time': 10,
        'missed_time': 60.0,
        'fine_explanations': [
            {
                'reason': 'shift_missed_time',
                'fine': 0.0,
                'reason_ext': (
                    'Пропущено 60.00 минут(ы) – упущенная сумма ' '0.00₽'
                ),
            },
        ],
        'fine_thresh_early': 10,
        'fine_thresh_late': 10,
        'fraud_on_start': True,
        'guarantee_loss_reasons': ['shift_early', 'shift_fraud', 'shift_late'],
        'is_guarantee': False,
        'is_self_employed': True,
        'is_newbie': False,
        'km_to_client_part': 0.0,
        'late_dropoff': 0.0,
        'late_pickup': 0,
        'late_return_lavka': 0,
        'late_start_min': 27.75,
        'long_to_rest_part': 0.0,
        'long_to_rest_thresh_m': 0.0,
        'min_number_of_orders_for_guarantee': 0,
        'missed_hours': 1.0,
        'number_of_fake_gps_orders': 0,
        'number_of_fraud_orders': 0,
        'number_of_lavka_orders': 0,
        'number_of_multiorders': 0,
        'number_of_orders': 0,
        'number_of_orders_with_fines': 0,
        'number_of_surged_orders': 0,
        'number_of_too_long_in_rest_orders': 0,
        'offline_time': 0.0,
        'online_time': 0.0,
        'pause_time': 0.0,
        'payment_to_cour_service': 0.0,
        'per_dropoff': 0.0,
        'per_fraud_status': 0.0,
        'per_hour_guarantee': 300.0,
        'per_km_to_client': 0.0,
        'per_long_to_rest': 0.0,
        'per_pickup': 0.0,
        'per_surge_order': 0.0,
        'pickup_part': 0.0,
        'planned_end_at': '2019-04-11T00:00:00+03:00',
        'planned_end_at_local_tz': '2019-04-11T00:00:00+03:00',
        'planned_hours': 9.0,
        'planned_start_at': '2019-04-10T15:00:00+03:00',
        'planned_start_at_local_tz': '2019-04-10T15:00:00+03:00',
        'pool_name': 'shop',
        'region_id': '1',
        'region_name': '',
        'salary_adjustments': 0.0,
        'salary_before_deductions': 2700.0,
        'salary_missed': 2700.0,
        'salary_on_hands': 0.0,
        'self_employed_tax_rate': 0,
        'self_employed_tax_sum': 0.0,
        'share_offline': 0.0,
        'shift_id': '1',
        'shift_type': 'planned',
        'surge_bonus': 0.0,
        'tips': 0.0,
        'to_rest_payable': 0.0,
        'unaccepted_orders': 0,
        'verified_flg': True,
        'weight_part': 0.0,
        'post': 'picker',
        'orders': [],
        'country_code': '',
        'guarantee': 0.0,
        'km_to_clients': 0.0,
        'km_to_rests': 0.0,
        'orders_part': 0.0,
        'timezone': 'Europe/Moscow',
    }

    response = await taxi_eats_logistics_performer_payouts.post(
        '/v1/offer', json=request,
    )

    assert response.status_code == 200
    assert sorted_response(response.json()) == sorted_response(
        expected_response,
    )
    assert check_pipeline_input.times_called == 1
    assert check_subject_context.times_called == 1

INSERT INTO eats_logistics_performer_payouts.subjects (id, external_id, subject_type_id)
VALUES
    (3, '3', 2),
    (10, '10', 2);
INSERT INTO eats_logistics_performer_payouts.calculation_results (subject_id, meta)
VALUES (
        3,
        '{
          "calculation_schema": "eda_pickup_dropoff",
          "surge_bonus": 0.0,
          "number_of_surged_orders": 0.0,
          "long_to_rest_part": 0.0,
          "date": "2022-05-23",
          "courier_type": "courier",
          "tips": 0.0,
          "shift_type": "planned",
          "is_self_employed": false,
          "country_code": "RU",
          "timezone": "Europe/Moscow",
          "shift_id": "123",
          "courier_id": "afd77890",
          "courier_name": "Василий Петрович",
          "courier_service_name": "ООО Тест",
          "unaccepted_orders": 0,
          "number_of_orders": 2,
          "orders_part": 250.00,
          "km_to_clients": 5.0,
          "km_to_client_part": 50.00,
          "km_to_rests": 1.0,
          "long_to_rest_part": 10.00,
          "salary_on_hands": 250.00,
          "is_newbie": false,
          "is_guarantee": true,
          "guarantee_loss_reasons": [],
          "guarantee": 200.00,
          "fine_amount": 0.0,
          "fine_explanations": [],
          "verified_flg": true,
          "planned_start_at_local_tz": "2022-05-23T19:30:00+00:00",
          "planned_end_at_local_tz": "2022-05-23T21:30:00+00:00",
          "offline_time": 0.0,
          "early_end_min": 0.0,
          "late_start_min": 0.0,
          "missed_time": 0.0,
          "number_of_orders_with_fines": 1,
          "number_of_multiorders": 0,
          "orders": [
            {
              "order_nr": "000000-000000",
              "fine_explanations": [
                {
                  "fine": 10.0,
                  "reason": "order_late_arrival_to_rest"
                },
                {
                  "fine": 10.0,
                  "reason": "order_late_arrival_to_client"
                }
              ]
            }
          ]
        }'::JSONB
    ), (
        10,
        '{
          "calculation_schema": "eda_blackbox",
          
          "total_payment": 420.0,
          "total_without_guarantee": 175.0,
          "add_to_guarantee": 225.0,
          
          "daily_payment": 120.0,
          "delivery_fee": 100.0,
          "tips": 20.0,
          
          "weekly_payment": 300.0,
          "orders_fixes": 55.0,
          "km": 6.0,
          "km_part": 120.0,
          
          "surge_bonus": 0.0,
          "number_of_surged_orders": 0.0,
          "long_to_rest_part": 0.0,
          "date": "2022-05-23",
          "courier_type": "courier",
          "shift_type": "planned",
          "is_self_employed": true,
          "country_code": "RU",
          "timezone": "Europe/Moscow",
          "shift_id": "123",
          "courier_id": "aacc8113",
          "courier_name": "Юрий Павлович",
          "courier_service_name": "ООО Тест",
          "unaccepted_orders": 0,
          "number_of_orders": 2,
          "orders_part": 250.00,
          "km_to_clients": 5.0,
          "km_to_client_part": 50.00,
          "km_to_rests": 1.0,
          "long_to_rest_part": 10.00,
          "salary_on_hands": 270.00,
          "is_newbie": false,
          "is_guarantee": true,
          "guarantee_loss_reasons": [],
          "guarantee": 400.00,
          "fine_amount": 0.0,
          "fine_explanations": [],
          "verified_flg": true,
          "planned_start_at_local_tz": "2022-05-23T19:30:00+00:00",
          "planned_end_at_local_tz": "2022-05-23T21:30:00+00:00",
          "offline_time": 0.0,
          "early_end_min": 8.0,
          "late_start_min": 0.0,
          "missed_time": 0.0,
          "number_of_orders_with_fines": 0,
          "number_of_multiorders": 0,
          "orders": [
            {
              "order_nr": "000000-000000",
              "earned_by_order": 175.00,
              "courier_demand_coefficient": 1.3,
              "fine_explanations": []
            }
          ]
        }'::JSONB
    );

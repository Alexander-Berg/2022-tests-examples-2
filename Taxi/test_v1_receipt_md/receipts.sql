INSERT INTO receipts.custom_receipts (
    order_id, type, receipt
) VALUES (
    '00000000000000000000000000000000', 'UNDEFINED',
    '{"total_price": 100500, "cashback": 15, "total_km": 100}'
 ),
 (
    '20000000000000000000000000000000', 'MD',
    '{
         "ride_cost": "913.0",
         "ride_discount_amount": "44.0",
         "ride_start_cost": "111.30000000000001",
         "ride_total_distance_km": "30.0",
         "ride_total_time_sec": 3600,
         "ride_waiting_cost": "300.0",
         "ride_waiting_time": 600,
         "ride_zones": [
            {
                "ride_distance_cost": "200.0",
                "ride_distance_km": "10.0",
                "ride_time_sec": 1800,
                "ride_time_cost": "30",
                "tariff_distance_price": "20.0000000001",
                "tariff_time_price": "1.0000000001",
                "zone_name": "spb"
            },
            {
                "ride_distance_cost": "300.0",
                "ride_distance_km": "20.0",
                "ride_time_sec": 1800,
                "ride_time_cost": "12.2",
                "tariff_distance_price": "20.0000000001",
                "tariff_time_price": "0.40000000001",
                "zone_name": "suburb"
            }
        ],
        "tariff_waiting_price": "0.5"
    }'
 )

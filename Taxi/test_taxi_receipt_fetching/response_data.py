MOLDOVA_CREATED_RESPONSE = {
    'code': 1001,
    'msg': (
        'Ride has being registered successfully! '
        '(\"Bon fiscal should be ready now!\")'
    ),
    'data': {
        'ride_uuid': 'xxxxxxxxxxxxxxxxxxxxxxxxxxx2',
        'partner_tax_id': '1001200003150',
        'partner_legal_name': 'S.C. UJ TAXI SRL',
        'partner_city': 'Or. Chisinau',
        'partner_legal_address': 'Str. Studentilor 2/4',
        'partner_car': 'Opel Zafira',
        'partner_plate_number': 'SDZ421',
        'ride_finish_dt': '2019-03-06 08:57:04',
        'service_description': 'TAXI',
        'ride_start_cost': '25',
        'ride_extra_cost': '2.33',
        'ride_cost': '100.11',
        'ride_total_km': '120',
        'customer_payment_type': 'cash',
        'customer_phone_last_digits': '5303',
        'ride_zones': [
            {
                'zone_name': 'Chisinau',
                'ride_km_amount': 6.564,
                'ride_price_km': 2.33,
                'ride_price_minute': 2.33,
            },
            {
                'zone_name': 'Ialoveni',
                'ride_km_amount': 6.564,
                'ride_price_km': 2.33,
                'ride_price_minute': 2.33,
            },
        ],
        'ride_waiting_time': '120',
        'ride_waiting_cost': '2.33',
        'ride_total_seconds': '134',
    },
}

MOLDOVA_RIDE_EXISTED_RESPONSE = {
    'code': 1002,
    'msg': 'Ride already exists! Cannot Recreate or edit!',
    'data': [],
}

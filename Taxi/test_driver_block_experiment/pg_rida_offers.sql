INSERT INTO offers
(
    offer_guid,
    user_guid,
    driver_guid,
    point_a,
    point_b,
    initial_price,
    offer_status,
    direction_map_url,
    used_bonus,
    available_bonus,
    passenger_seen_complete_screen,
    price_sequence
)
VALUES
    (
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G',
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
        'Стремянный пер., 35',
        'Житная ул., 6',
        156.00,
        'COMPLETE',
        'https://maps.googleapis.com/maps/api',
        0.00,
        0.00,
        0,
        1
    ),
    (
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5H',
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
        'Стремянный пер., 35',
        'Житная ул., 6',
        156.00,
        'DRIVER_CANCELLED',
        'https://maps.googleapis.com/maps/api',
        0.00,
        0.00,
        0,
        1
    ),
    (
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5I',
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B',
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C',
        'Стремянный пер., 35',
        'Житная ул., 6',
        156.00,
        'PASSENGER_CANCELLED',
        'https://maps.googleapis.com/maps/api',
        0.00,
        0.00,
        0,
        1
    );


INSERT INTO push_notification_tokens
(id, user_guid, language_id, token, hash, device_type, application_id, application_version)
VALUES
    (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 1 , 'firebase_token', '', '', '', ''),
    (5678, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', 1, 'firebase_token', '', '', '', '');

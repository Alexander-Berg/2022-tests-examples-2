INSERT INTO offers
(
    id,
    offer_guid,
    user_guid,
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
        1,                                      --id
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', --offer_guid
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', --user_guid
        'Стремянный пер., 35',                  --point_a
        'Житная ул., 6',                        --point_b
        156.00,                                 --initial_price
        'COMPLETE',                             --offer_status
        'https://maps.googleapis.com/maps/api', --direction_map_url
        0.00,                                   --used_bonus
        0.00,                                   --available_bonus
        0,                                      --passenger_seen_complete_screen
        1                                       --price_sequence
    );

INSERT INTO push_notification_tokens
(id, user_guid, language_id, token, hash, device_type, application_id, application_version)
VALUES
    (1234, '9373F48B-C6B4-4812-A2D0-413F3AFBAD5B', 1 , 'firebase_token', '', '', '', '');

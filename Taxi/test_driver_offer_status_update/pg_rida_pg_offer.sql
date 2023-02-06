INSERT INTO offers
    (
        id,
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
        1,                                      --id
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5G', --offer_guid
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5E', --user_guid
        '9373F48B-C6B4-4812-A2D0-413F3AFBAD5C', --driver_guid
        'Стремянный пер., 35',                  --point_a
        'Житная ул., 6',                        --point_b
        156.00,                                 --initial_price
        'PASSENGER_CANCELLED',                  --offer_status
        'https://maps.googleapis.com/maps/api', --direction_map_url
        0.00,                                   --used_bonus
        0.00,                                   --available_bonus
        0,                                      --passenger_seen_complete_screen
        1                                       --price_sequence
    );

INSERT INTO user_codes
(
    user_id,
    code,
    qr_code,
    expires_at
)
VALUES
(
    177043222,
    '111111',
    'YNDX17bd2a3c7db44373822cc291d09b86bc',
    '2022-02-22 22:03:00.000000Z'
);

INSERT INTO terminal_tokens
(
    id,
    token,
    dek,
    place_id
)
VALUES
(
    'terminal_id',
    '6j3/BEioT3vgvNa9ca2U7e+DuO1dqEs9x8hShzbet/I=',
    'pbrXGGxr9JdNTEsQeCjss+gc/8S9hyYndVkxdNw0B5e3B0CV4WXAyCZZBcIP7aqxLRCql1nNVjeTXDBBNCYQYQ==',
    '146'
),
(
    'terminal_id_2',
    '6j3/BEioT3vgvNa9ca2U7e+DuO1dqEs9x8hShzbet/I=',
    'pbrXGGxr9JdNTEsQeCjss+gc/8S9hyYndVkxdNw0B5e3B0CV4WXAyCZZBcIP7aqxLRCql1nNVjeTXDBBNCYQYQ==',
    '147'
);

INSERT INTO places
(
    place_id,
    balance_client_id,
    name,
    region_id,
    address_city,
    address_short,
    address_comment,
    brand_id,
    brand_name,
    location
)
VALUES
(
    '146',
    '146',
    'Place 146',
    '1',
    'address city',
    'address short',
    'address comment',
    '777',
    'brand 777',
    '(52,39)'
),
(
    '147',
    '147',
    'Place 147',
    '1',
    'address city',
    'address short',
    'address comment',
    '777',
    'brand 777',
    '(52.569089,39.60258)'
);;

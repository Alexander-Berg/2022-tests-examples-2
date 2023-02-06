INSERT INTO restaurants (
    place_id,
    slug,
    name,
    pos_type,
    logo_link,
    description,
    enabled,
    tips_link_fallback,
    billing_client_id,
    geo_point,
    region_id,
    personal_tin_id,
    last_time_table_check
)
VALUES
(
    'place_id__1',
    'place_id__1_slug',
    'Самый тестовый ресторан',
    'iiko',
    '135516/147734d81d1de576476c6a217679e1c29f83eeb7',
    'Он настолько тестовый, что его можно только тестировать',
    TRUE,
    'some_tips_link',
    'billing_client_id__1',
    '(39.022872,45.056503)'::POINT,
    13,
    'personal_tin_id__1',
    '2022-05-16T10:00:00+00:00'
 )
;

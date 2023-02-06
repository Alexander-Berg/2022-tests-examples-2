INSERT INTO partner (category, name, logo, comment, created_by, created_at, updated_by, updated_at)
VALUES (
        'food',
        'Big zombie shop',
        'https://example.com/image.jpg',
        'Some comment text',
        'valery',
        '2019-05-26 19:10:25+3',
        'valery',
        '2019-05-26 19:10:25+3'
       );

INSERT INTO location(business_oid, partner_id, longitude, latitude, country, city, address, name, work_time_intervals,tz_offset)
VALUES (
        123456,
        (SELECT id FROM partner WHERE name = 'Big zombie shop'),
        40.5,
        80.4,
        'Russia',
        'Moscow',
        'Москва, Лубянка, 5',
        'Big zombie shop',
        '[]'::JSONB,
        0
       );

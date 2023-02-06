INSERT INTO partner (category, name, logo, comment, created_by, created_at, updated_by, updated_at)
VALUES ('food',
        'Грибница',
        'https://example.com/image.jpg',
        'Ленин - гриб',
        'Ильич',
        '2019-05-26 19:10:25+3',
        'Ильич',
        '2019-05-26 19:10:25+3'),
       ('service',
        'Радиоволна',
        'http://bronevik.com/im.png',
        'То же, что и гриб',
        'Ульянов',
        '2019-05-28 19:10:25+3',
        'Ульянов',
        '2019-07-28 19:10:25+3')
;

INSERT INTO deal(partner_id,
                 title,
                 description_title,
                 comment,
                 consumer,
                 kind,
                 kind_json,
                 enabled,
                 begin_at,
                 finish_at,
                 created_by,
                 updated_by)
VALUES
--- drivers
(1, 'First', 'some', NULL, 'driver', 'fix_price', '{
  "old_price": "5",
  "new_price": "4", "old_curr":"RUB", "new_curr":"RUB"
}'::jsonb, true, '2019-05-26 19:10:25+3', NULL, 'Ильич', 'Ульянов'),
(1, 'Second', 'some', NULL, 'courier', 'coupon', '{
  "text": "Hee",
  "price": "5", "currency":"RUB"
}'::jsonb, true, '2019-05-26 19:10:25+3', '2020-05-26 19:10:25+3', 'Ильич', 'Ульянов'),
(2, 'First', 'some', 'test comment', 'driver', 'discount', '{
  "text": "Some",
  "percent": "10"
}'::jsonb, true, '2019-05-26 19:10:25+3', NULL, 'Ильич', 'Ульянов');

INSERT INTO location(business_oid, partner_id, longitude, latitude, country, city, address, name, work_time_intervals, tz_offset)
VALUES (101,
        1,
        40.5,
        80.4,
        'Russia',
        'Moscow',
        'Москва, Лубянка, 5',
        'Big zombie shop',
        '[]'::JSONB,
        0),
       (102,
        1,
        40.5,
        80.4,
        'Russia',
        NULL,
        'Россия, Лубянка, 5',
        'Cataclyzm',
        '[]'::JSONB,
        0),
       (103,
        2,
        40.5,
        80.4,
        NULL,
        'Moscow',
        'Москва, Лубянка, 5',
        'Big zombie shop',
        '[]'::JSONB,
        0)
;

INSERT INTO deal_consumer_subclass(deal_id, subclass)
VALUES (1, 'silver'),
       (2, '1'),
       (2, '3'),
       (2, '5'),
       (3, 'bronze'),
       (3, 'silver'),
       (3, 'platinum');


INSERT INTO partner (category, name, logo, comment, created_by, created_at, updated_by, updated_at)
VALUES (
        'food',
        'Грибница',
        'https://example.com/image.jpg',
        'Ленин - гриб',
        'Ильич',
        '2019-05-26 19:10:25+3',
        'Ильич',
        '2019-05-26 19:10:25+3'
       ),
       (
        'service',
        'Радиоволна',
        'http://bronevik.com/im.png',
        'То же, что и гриб',
        'Ульянов',
        '2019-05-28 19:10:25+3',
        'Ульянов',
        '2019-07-28 19:10:25+3'
       ),
       (
        'food',
        'Мухоморье',
        NULL,
        '',
        'Ульянов',
        '2019-05-29 19:10:25+3',
        'Ульянов',
        '2019-07-29 19:10:25+3'
       ),
       (
        'food',
        'не действующие офферы',
        NULL,
        '',
        'Ульянов',
        '2019-05-29 19:10:25+3',
        'Ульянов',
        '2019-07-29 19:10:25+3'
       )
;

INSERT INTO deal(
    partner_id,
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
    updated_by
) VALUES
(1, 'Food','some', 'a', 'driver', 'fix_price', '{"discount": 5}'::jsonb, true, NOW()-INTERVAL '5 day', NULL, 'Ильич', 'Ильич'),
(1, 'Food','some', 'a','driver', 'fix_price', '{"discount": 5}'::jsonb, true, NOW()-INTERVAL '5 day', NULL, 'Ильич', 'Ильич'),
(1, 'Food','some', 'a','driver', 'fix_price', '{"discount": 5}'::jsonb, true, NOW()+INTERVAL '1 month', NULL, 'Ильич', 'Ильич'),
(1, 'Food','some', 'a','driver', 'fix_price', '{"discount": 5}'::jsonb, false, NOW()-INTERVAL '5 day', NULL, 'Ильич', 'Ильич'),
(2, 'Service','some','a', 'driver', 'fix_price', '{"discount": 5}'::jsonb, true, NOW()-INTERVAL '1 day', NULL, 'Ильич', 'Ильич'),
(2, 'Service', 'some','a','driver', 'fix_price', '{"discount": 5}'::jsonb, false, NOW()-INTERVAL '1 day', NULL, 'Ильич', 'Ильич'),
(4, 'НЕ ДЕЙСТВУЕТ', 'some','a','driver', 'fix_price', '{"discount": 5}'::jsonb, true, NOW()+INTERVAL '1 day', NULL, 'Ильич', 'Ильич'),
(4, 'НЕ ДЕЙСТВУЕТ', 'some','a','driver', 'fix_price', '{"discount": 5}'::jsonb, true, NOW()-INTERVAL '30 day', NOW()-INTERVAL '15 day', 'Ильич', 'Ильич'),
(4, 'НЕ ДЕЙСТВУЕТ', 'some','a','driver', 'fix_price', '{"discount": 5}'::jsonb, false, NOW()-INTERVAL '30 day', NOW()+INTERVAL '15 day', 'Ильич', 'Ильич')
;

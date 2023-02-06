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
                 consumer,
                 kind,
                 kind_json,
                 enabled,
                 begin_at,
                 created_by,
                 updated_by)
VALUES
--- drivers
(1, 'First', 'some', 'driver', 'fix_price', '{
  "old_price": "5",
  "new_price": "4", "old_curr":"RUB","new_curr":"RUB"
}'::jsonb, true, NOW() - INTERVAL '5 day', 'Ильич', 'Ульянов'),
(1, 'Second', 'some', 'driver', 'coupon', '{
  "text": "Hee",
  "price": "5", "currency":"RUB"
}'::jsonb, true, NOW() - INTERVAL '5 day', 'Ильич', 'Ульянов'),
(1, 'Third', 'some', 'driver', 'discount', '{
  "percent": "5"
}'::jsonb, true, NOW() + INTERVAL '1 month', 'Ильич', 'Ильич'),
(1, 'Fourth', 'some', 'driver', 'fix_price', '{
  "old_price": "5",
  "new_price": "4", "old_curr":"RUB","new_curr":"RUB"
}'::jsonb, false, NOW() - INTERVAL '5 day', 'Ильич', 'Ильич'),
(2, 'Fifth', 'some', 'driver', 'discount', '{
  "percent": "5"
}'::jsonb, true, NOW() - INTERVAL '1 day', 'Ильич', 'Ульянов'),
(2, 'Six', 'some', 'driver', 'coupon', '{
  "price": "5.08", "currency":"RUB"
}'::jsonb, false, NOW() - INTERVAL '1 day', 'Ильич', 'Ильич'),
--- couriers
(1, 'First', 'some', 'courier', 'fix_price', '{
  "old_price": "5",
  "new_price": "4", "old_curr":"RUB","new_curr":"RUB"
}'::jsonb, true, NOW() - INTERVAL '5 day', 'Ильич', 'Ульянов'),
(1, 'Second', 'some', 'courier', 'coupon', '{
  "text": "Hee",
  "price": "5", "currency":"RUB"
}'::jsonb, true, NOW() - INTERVAL '5 day', 'Ильич', 'Ульянов'),
(1, 'Third', 'some', 'courier', 'discount', '{
  "percent": "5"
}'::jsonb, true, NOW() + INTERVAL '1 month', 'Ильич', 'Ильич'),
(1, 'Fourth', 'some', 'courier', 'fix_price', '{
  "old_price": "5",
  "new_price": "4", "old_curr":"RUB","new_curr":"RUB"
}'::jsonb, false, NOW() - INTERVAL '5 day', 'Ильич', 'Ильич'),
(2, 'Fifth', 'some', 'courier', 'discount', '{
  "percent": "5"
}'::jsonb, true, NOW() - INTERVAL '1 day', 'Ильич', 'Ульянов'),
(2, 'Six', 'some', 'courier', 'coupon', '{
  "price": "5.08", "currency":"RUB"
}'::jsonb, false, NOW() - INTERVAL '1 day', 'Ильич', 'Ильич')
;

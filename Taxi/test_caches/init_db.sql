INSERT INTO partner (category, name, logo, created_by, created_at, updated_by, updated_at)
VALUES ('food',
        'Грибница',
        'https://example.com/image.jpg',
        'Ильич',
        '2019-05-26 19:10:25+3',
        'Ильич',
        '2019-05-26 19:10:25+3'),
       ('service',
        'Радиоволна',
        'http://bronevik.com/im.png',
        'Ульянов',
        '2019-05-28 19:10:25+3',
        'Ульянов',
        '2019-07-28 19:10:25+3'),
       ('help',
        'Водкария',
        'http://vodka.ru/im.png',
        'Ульянов',
        '2019-05-28 19:10:25+3',
        'Ульянов',
        '2019-07-28 19:10:25+3')
;

WITH loc(business_oid, partner_id, name, latitude, longitude, tzinfo, wk_times) as (VALUES
                  --- included
                  (11, 1, 'Грибница1', 55, 37.5, 10800, '[{"from": 1575039000, "to":1575069000}]'),
                  --- removed by deal
                  (12, 1, 'Грибница2', 55, 37.5, 10800, '[{"from": 1575039000, "to":1575069000}]'),
                  --- removed by range
                  (13, 1, 'Грибница3', 55, 90, 10800, '[{"from": 1575039000, "to":1575069000}]'),
                  --- removed `by working time`
                  (14, 1, 'Грибница4', 55, 37.5, 10800, '[{"from": 1575069000, "to":1575079000}]'),
                  (21, 2, 'Радиоволна1', 55, 37.5, 21600, '[{"from": 1575039000, "to":1575069000}]'),
                  (22, 2, 'Радиоволна2', 55, 37.5, 21600, '[{"from": 1575039000, "to":1575069000}]'),
                  (23, 2, 'Радиоволна3', 55, 90, 21600, '[{"from": 1575039000, "to":1575069000}]'),
                  (24, 2, 'Радиоволна4', 55, 37.5, 21600, '[{"from": 1575069000, "to":1575080000}]'),
                  --- Водкария is removed by loyalty
                  (31, 3, 'Водкария1', 55, 37.5, 10800, '[{"from": 1575039000, "to":1575069000}]'),
                  (32, 3, 'Водкария2', 55, 37.5, 10800, '[{"from": 1575039000, "to":1575069000}]'),
                  (33, 3, 'Водкария3', 55, 90, 10800, '[{"from": 1575039000, "to":1575069000}]'),
                  (34, 3, 'Водкария4', 55, 37.5, 10800, '[{"from": 1575039000, "to":1575069000}]')
)
INSERT
INTO location(business_oid,
              partner_id,
              longitude,
              latitude,
              name,
              address,
              work_time_intervals,
              tz_offset,
              updated_at)
SELECT business_oid,
       partner_id,
       longitude,
       latitude,
       name,
       'Simple test address',
       wk_times::jsonb,
       tzinfo,
       '2019-07-28 19:10:25+3'
FROM loc;

WITH dealdata(
              id,
              partner_id,
              consumer,
              enabled,
              kind, kind_json,
              map_pin_text,
              antitags
    ) as (
    VALUES (11, 1, 'driver', TRUE, 'discount', '{"percent":"15"}', NULL, ARRAY['antitag_1']),
           (12, 1, 'driver', FALSE, 'discount', '{"percent":"20"}', 'MapText', ARRAY[]::TEXT[]),
           (21, 2, 'driver', TRUE, 'discount', '{"percent":"20"}', 'MapText', ARRAY[]::TEXT[]),
           (22, 2, 'driver', TRUE, 'coupon', '{"price":"700", "currency":"RUB"}', NULL, ARRAY['antitag_1', 'antitag_2']),
           (31, 3, 'driver', TRUE, 'discount', '{"percent":"20"}', 'MapText', ARRAY[]::TEXT[]),
           (32, 3, 'courier', TRUE, 'discount', '{"percent":"20"}', NULL, ARRAY[]::TEXT[])
)
INSERT
INTO deal(id, partner_id, consumer, enabled, kind, kind_json, map_pin_text, created_by, updated_by, begin_at, title,
          description_title, updated_at, antitags)
SELECT id,
       partner_id,
       consumer,
       enabled,
       kind,
       kind_json::jsonb,
       map_pin_text,
       'Padda',
       'Padda',
       '2014-04-04 20:00:00-07'::timestamptz,
       'Some title',
       'Some desc title',
       '2019-07-28 19:10:25+3',
       antitags
from dealdata;

INSERT INTO active_deal_location(deal_id, location_id)
VALUES (11, 11),
       (11, 13),
       (11, 14),
       (21, 23),
       (21, 24),
       (22, 21),
       (22, 22),
       (22, 23),
       (22, 24),
       (31, 31),
       (31, 32),
       (31, 33),
       (31, 34),
       (32, 31),
       (32, 32),
       (32, 33),
       (32, 34)
;

INSERT INTO deal_consumer_subclass(deal_id, subclass)
VALUES (11, 'bronze'),
       (12, 'bronze'),
       (21, 'bronze'),
       (22, 'bronze'),
       (31, 'platinum'),
       (32, '3')
;

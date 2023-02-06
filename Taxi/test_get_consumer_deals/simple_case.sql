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
        '2019-07-28 19:10:25+3'),
       ('vat',
        'Маковое море',
        'http://mac.more.ru/im.png',
        'Грибной Ленин',
        '2019-05-28 19:10:25+3',
        'Грибной Ленин',
        '2019-07-28 19:10:25+3')
;

WITH loc(business_oid, partner_id, name, latitude, longitude, tzinfo, wk_times) as (VALUES
                                                                                        --- included
                                                                                        (11, 1, 'Грибница1', 55, 37.5,
                                                                                         10800,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        --- removed by deal
                                                                                        (12, 1, 'Грибница2', 55, 37.5,
                                                                                         10800,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        --- removed by range
                                                                                        (13, 1, 'Грибница3', 55, 90,
                                                                                         10800,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        --- removed `by working time`
                                                                                        (14, 1, 'Грибница4', 55, 37.5,
                                                                                         10800,
                                                                                         '[{"from": 1575069000, "to":1575079000}]'),
                                                                                        (21, 2, 'Радиоволна1', 55, 37.5,
                                                                                         21600,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        (22, 2, 'Радиоволна2', 55, 37.5,
                                                                                         21600,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        (23, 2, 'Радиоволна3', 55, 90,
                                                                                         21600,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        (24, 2, 'Радиоволна4', 55, 37.5,
                                                                                         21600,
                                                                                         '[{"from": 1575069000, "to":1575080000}]'),
                                                                                        --- Водкария is removed by loyalty
                                                                                        (31, 3, 'Водкария1', 55, 37.5,
                                                                                         10800,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        (32, 3, 'Водкария2', 55, 37.5,
                                                                                         10800,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        (33, 3, 'Водкария3', 55, 90,
                                                                                         10800,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        (34, 3, 'Водкария4', 55, 37.5,
                                                                                         10800,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),

                                                                                        (41, 4, 'Мак1', 55, 37.5, 21600,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        (42, 4, 'Мак2', 55, 37.5, 21600,
                                                                                         '[{"from": 1575039000, "to":1575069000}]'),
                                                                                        (43, 4, 'Мак3', 55, 37.5, 21600,
                                                                                         '[{"from": 1575039000, "to":1575069000}]')
)
INSERT
INTO location(business_oid,
              partner_id,
              longitude,
              latitude,
              name,
              address,
              work_time_intervals,
              tz_offset)
SELECT business_oid,
       partner_id,
       longitude,
       latitude,
       name,
       'Simple test address',
       wk_times::jsonb,
       tzinfo
FROM loc;

WITH dealdata(
              id,
              partner_id,
              consumer,
              enabled,
              kind, kind_json
    ) as (
    VALUES (11, 1, 'driver', TRUE, 'discount', '{"percent":"15"}'), --- Allowed only in one location
           (12, 1, 'driver', FALSE, 'discount', '{"percent":"20"}'),
           (21, 2, 'driver', TRUE, 'discount', '{"percent":"20"}'), --- Allowed only in far away
           (22, 2, 'driver', TRUE, 'coupon', '{"price":"700", "currency":"RUB"}'),
           (31, 3, 'driver', TRUE, 'discount', '{"percent":"20"}'), --- NOT allowed for bronze
           (32, 3, 'courier', TRUE, 'discount', '{"percent":"20"}')
)
INSERT
INTO deal(id, partner_id, consumer, enabled, kind, kind_json, created_by, updated_by, begin_at, title,
          description_title)
SELECT id,
       partner_id,
       consumer,
       enabled,
       kind,
       kind_json::jsonb,
       'Padda',
       'Padda',
       '2014-04-04 20:00:00-07'::timestamptz,
       'Some title',
       'Some desc title'
FROM dealdata;

/* For rebates testing */
WITH dealdata(
              id,
              partner_id,
              map_pin_text,
              kind, kind_json
    ) as (
    VALUES (41, 4, NULL, 'discount', '{"percent":"20"}'),
           (42, 4, NULL, 'coupon', '{"price":"700", "currency":"RUB"}'),
           (43, 4, 'Other map text', 'coupon', '{"price":"700", "currency":"RUB"}')
)
INSERT
INTO deal(id, partner_id, consumer, enabled, kind, kind_json, map_pin_text, created_by, updated_by, begin_at, title,
          description_title)
SELECT id,
       partner_id,
       'driver',
       TRUE,
       kind,
       kind_json::jsonb,
       map_pin_text,
       'Padda',
       'Padda',
       '2014-04-04 20:00:00-07'::timestamptz,
       'Some title',
       'Some desc title'
FROM dealdata;

INSERT
INTO active_deal_location(deal_id, location_id)
SELECT deal.id, location.business_oid
FROM deal
         JOIN location ON deal.partner_id = location.partner_id
WHERE (deal.id, location.business_oid) NOT IN (
                                               (11, 12),
                                               (21, 21),
                                               (21, 22),
                                               (41, 42),
                                               (43, 41),
                                               (43, 42)
    )
;

INSERT INTO deal_consumer_subclass(deal_id, subclass)
VALUES (11, 'bronze'),
       (12, 'bronze'),
       (21, 'bronze'),
       (22, 'bronze'),
       (31, 'platinum'),
       (32, '3'),
       (41, 'bronze'),
       (42, 'bronze'),
       (43, 'bronze')
;

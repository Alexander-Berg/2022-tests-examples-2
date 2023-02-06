INSERT INTO state.offers
  (
    offer_id,
    valid_until,
    image_id,
    description,
    created,
    origin
  )
VALUES
  (
    1001,
    '2018-11-27T22:00:00+0000',
    'icon_1',
    'some text #1',
    '2018-11-26T22:00:00+0000',
    ('reposition-relocator')::db.offer_origin
  )
;

INSERT INTO state.offers_metadata
  (
    offer_id,
    airport_queue_id
  )
VALUES
  (
    1001,
    'airport_q1'
  )
;

INSERT INTO settings.points
  (
    point_id,
    mode_id,
    driver_id_id,
    updated,
    name,
    address,
    city,
    location,
    offer_id
  )
VALUES
  (
    1001,
    1488,
    IdId('driverSS','1488'),
    '11-26-2018',
    'pg_point_1',
    'some address_1',
    'Postgresql_1',
    (31, 61)::db.geopoint,
    1001
  )
;

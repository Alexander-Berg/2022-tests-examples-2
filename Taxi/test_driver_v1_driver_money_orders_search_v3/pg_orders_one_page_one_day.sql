INSERT INTO orders_0 (
  park_id,
  id,
  number,
  driver_id,
  date_booking,
  date_create,
  status,
  payment,
  provider,
  address_from,
  category
)
VALUES (
  'park_id_0',--park_id
  'order6',--id
  '1',--number
  'driver',--driver_id
  '2019-05-10T16:18:00',--date_booking
  '2019-05-10T16:18:00',--date_create
  50,--status
  1,--payment cashless
  2,--provider
  '{"Street":"Вильнюсская улица, 7к2","Porch":"","Region":"","Lat":55.6022246645,"Lon":37.5224489641}',--address_from,
  'econom'
),
(
  'park_id_0',--park_id
  'order5',--id
  '2',--number
  'driver',--driver_id
  '2019-05-10T13:26:00',--date_booking
  '2019-05-10T13:26:00',--date_create
  50,--status
  0,--payment
  2,--provider
  '{"Street":"Рядом с: улица Островитянова, 47","Porch":"","Region":"","Lat":55.6348324304,"Lon":37.541191945}',--address_from,
  'business'
),
(
  'park_id_0',--park_id
  'order4',--id
  '3',--number
  'driver',--driver_id
  '2019-05-10T12:26:00',--date_booking
  '2019-05-10T12:26:00',--date_create
  50,--status
  1,--payment cashless
  2,--provider
  '{"Street":"Вильнюсская улица, 7к2","Porch":"","Region":"","Lat":55.6022246645,"Lon":37.5224489641}',--address_from,
  'business'
),
-- new page
-- order with same date_booking
(
  'park_id_0',--park_id
  'order3',--id
  '3',--number
  'driver',--driver_id
  '2019-05-08T12:26:00',--date_booking
  '2019-05-08T12:26:00',--date_create
  50,--status
  0,--payment
  2,--provider
  '{"Street":"Вильнюсская улица, 7к2","Porch":"","Region":"","Lat":55.6022246645,"Lon":37.5224489641}',--address_from,
  'econom'
),
(
  'park_id_0',--park_id
  'order2',--id
  '3',--number
  'driver',--driver_id
  '2019-05-08T11:26:00',--date_booking
  '2019-05-08T11:26:00',--date_create
  50,--status
  0,--payment
  2,--provider
  '{"Street":"Вильнюсская улица, 7к2","Porch":"","Region":"","Lat":55.6022246645,"Lon":37.5224489641}',--address_from,
  'econom'
),
(
  'park_id_0',--park_id
  'order1',--id
  '3',--number
  'driver',--driver_id
  '2019-05-08T10:26:00',--date_booking
  '2019-05-08T10:26:00',--date_create
  50,--status
  0,--payment
  2,--provider
  '{"Street":"Вильнюсская улица, 7к2","Porch":"","Region":"","Lat":55.6022246645,"Lon":37.5224489641}',--address_from,
  'econom'
);

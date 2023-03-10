INSERT INTO eats_report_storage.rad_quality (
    place_id,
    brand_id,
    name,
    address,
    rating,
    orders,
    avg_check,
    cancel_rating,
    pict_share,
    plus_flg,
    dish_as_gift_flg,
    discount_flg,
    second_for_free_flg,
    pickup_flg,
    mercury_flg)
VALUES
  (
     1,
     1,
     'Макдоналдс1',
     'улица Декабристов, 11',
     3.3,
     3,
     3.3,
     3.3,
     3.3,
     true,
     false,
     NULL,
     NULL,
     NULL,
     NULL
  ),
  (
     4,
     4,
     'Макдоналдс2',
     'улица Декабристов, 22',
     4.4,
     4,
     4.4,
     4.4,
     4.4,
     true,
     false,
     NULL,
     NULL,
     NULL,
     NULL
  );

INSERT INTO eats_report_storage.rad_suggests (
    suggest,
    prioriy,
    place_id)
VALUES
  (
    'cancels',
    3.3,
    1
  ),
  (
    'pict_share',
    4.4,
    2
  );

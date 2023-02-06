INSERT INTO cart.carts (cart_id, updated, created, checked_out)
VALUES
       ('0913571f-ec64-4052-ad8e-7d0351c82998',
        '2020-02-20T15:55:01.4183+03:00'::timestamptz,
        '2020-02-20T15:55:01.4183+03:00'::timestamptz, true),
       ('3913571f-ec64-2052-ad8e-7d0351c8229a',
        '2020-02-28T15:55:01.4183+03:00'::timestamptz,
        '2020-02-28T15:55:01.4183+03:00'::timestamptz, true),
       ('c19ef2cc-0c06-450c-b07f-175d8ef9d95f',
        '2020-02-28T15:55:02.084402+03:00'::timestamptz,
        '2020-02-20T15:55:02.084402+03:00'::timestamptz, false),
       ('169e974f-9218-4534-9835-94e04ebfc4a1',
        '2020-02-26T15:11:02.084402+03:00'::timestamptz,
        '2020-02-20T15:11:02.084402+03:00'::timestamptz, false),
       ('d5580fbb-5719-409a-b891-4001ef049682',
        '2020-02-21T15:55:02.084402+03:00'::timestamptz,
        '2020-02-20T15:55:02.272179+03:00'::timestamptz, false);

INSERT INTO cart.cart_items (cart_id, item_id, updated)
VALUES 
       ('d5580fbb-5719-409a-b891-4001ef049682',
        '1234',
        '2020-02-20T15:55:02.570363+03:00'::timestamptz),
        ('c19ef2cc-0c06-450c-b07f-175d8ef9d95f',
        '1234',
        '2020-02-20T15:55:02.570363+03:00'::timestamptz);

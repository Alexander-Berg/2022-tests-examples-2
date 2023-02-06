INSERT INTO eats_restapp_promo.place_plus_activation
(place_id, status, cashback, starts, ends, updated_at)
VALUES
    ('1', 'active', 10.0, '2021-08-01 00:00:00 +03:00', '2123-10-10 00:00:00 +03:00', current_timestamp),
    ('2', 'active', 5.0, '2021-08-01 00:00:00 +03:00', '2021-08-02 00:00:00 +03:00', current_timestamp);

INSERT INTO eats_restapp_promo.promos(
    promo_id,
    place_ids,
    promo_type,
    status,
    starts,
    ends,
    requirements,
    bonuses,
    schedule,
    discount_task_id,
    discount_ids,
    set_at)
VALUES
    (
        1,
        '{1}',
        'free_delivery',
        'enabled',
        '2021-08-01 00:00:00 +03:00'::timestamptz,
        '2021-10-11 00:00:00 +03:00'::timestamptz,
        '{}',
        '{}',
        '{}',
        '1',
        '{1}',
        '2021-08-01 00:00:00 +03:00'::timestamptz
    ),
    (
        3,
        '{3}',
        'free_delivery',
        'enabled',
        '2021-08-01 00:00:00 +03:00'::timestamptz,
        '2021-10-11 00:00:00 +03:00'::timestamptz,
        '{"requirements": []}',
        '{"bonuses": []}',
        '{"schedule": {}}',
        '1',
        '{1}',
        '2021-08-01 00:00:00 +03:00'::timestamptz
    );

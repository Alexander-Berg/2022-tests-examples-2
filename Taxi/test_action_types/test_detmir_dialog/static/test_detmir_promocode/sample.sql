INSERT INTO supportai.actions_miscs (id, project_id, misc_slug, misc_name)
VALUES
(1, 'detmir_dialog', 'detmir_promocodes', 'Промокоды ДМ'),
(2, 'detmir_ne_dialog', 'detmir_promocodes', 'Промокоды ДМ');


INSERT INTO supportai.actions_miscs_container (id, misc_slug, misc)
VALUES
(1, 'detmir_promocodes',
$$
{
    "promocode_code": "XXX-01-XXXX",
    "promocode_amount": 99999,
    "promocode_expired_at": "2021-12-31 00:00:00.000000",
    "promocode_min_order_sum": 300,
    "order_id": "gained"
}
$$
),
(2, 'detmir_promocodes',
$$
{
    "promocode_code": "XXX-01-XXXX",
    "promocode_amount": 99999,
    "promocode_expired_at": "2021-12-31 00:00:00.000000",
    "promocode_min_order_sum": 300,
    "order_id": null
}
$$
),
(3, 'detmir_promocodes',
$$
{
    "promocode_code": "XXX-01-XXXX",
    "promocode_amount": 99999,
    "promocode_expired_at": "2021-12-31 00:00:00.000000",
    "promocode_min_order_sum": 300,
    "order_id": null
}
$$
);

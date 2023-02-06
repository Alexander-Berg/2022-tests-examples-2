INSERT INTO supportai.actions_miscs (id, project_id, misc_slug, misc_name)
VALUES
(1, 'litres_dialog', 'litres_dialog_promocodes', 'Промокоды Литрес'),
(2, 'not_litres_dialog', 'litres_dialog_promocodes', 'Промокоды Литрес');


INSERT INTO supportai.actions_miscs_container (id, misc_id, misc)
VALUES
(1, 1,
$$
{
    "promocode_code": "XXX-01-XXXX",
    "promocode_expired_at": "2022-05-11 00:00:00.000000",
    "ticket_id": "gained"
}
$$
),
(2, 1,
$$
{
    "promocode_code": "XXX-02-XXXX",
    "promocode_expired_at": "2022-05-11 00:00:00.000000",
    "ticket_id": null
}
$$
),
(3, 1,
$$
{
    "promocode_code": "XXX-03-XXXX",
    "promocode_expired_at": "2022-05-11 00:00:00.000000",
    "ticket_id": null
}
$$
),
(4, 2,
$$
{
    "promocode_code": "XXX-04-XXXX",
    "promocode_expired_at": "2022-05-11 00:00:00.000000",
    "ticket_id": null
}
$$
);

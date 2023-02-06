INSERT INTO yt.report_orders_moderation
    (
        "order_id",
        "park_id",
        "driver_id",
        "date_end",
        "cost_total"
    )
VALUES
(
    'aaq3bcras60d499f8ac57tc52aj8fs9p',
    '7ad36bc7560449998acbe2c57a75c293',
    '1ash66r567j4ogt98acb22cg7ai5c123',
    '2020-09-22 00:00:00+03:00',
    100
)
;
INSERT INTO public.orders_moderation_status
    (
        "park_id",
        "order_id",
        "status",
        "chat_id",
        "date_end"
    )
VALUES
    (
        '7ad36bc7560449998acbe2c57a75c293',
        'aaq3bcras60d499f8ac57tc52aj8fs9p',
        'active',
        NULL,
        '2020-09-22 00:00:00+03:00'
    )
;

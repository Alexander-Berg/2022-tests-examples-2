INSERT INTO eats_ordershistory.orders (
    "order_id", "order_source", "eats_user_id", "taxi_user_id",
    "yandex_uid", "place_id", "status", "delivery_location",
    "total_amount", "is_asap", "cancel_reason", "created_at",
    "delivered_at", "order_type", "original_total_amount",
    "currency", "shipping_type", "delivery_type", "cancelled_at",
    "ready_to_delivery_at", "taken_at"
)
VALUES
    (
        'euid-1', 'eda', 1, 2,
        'ya1', '12525', 'taken', '35,64',
        '23523', '0', '2523sdsdga sdg asdgdg', '2020-06-15T11:00:00Z',
        NULL, 'native', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
  ,(
        'euid-2', 'lavka', 2, 1,
        'ya2', '12525', 'sent', '35,64',
        '23523', '0', '2523sdsdga sdg asdgdg', '2020-06-15T10:00:00Z',
        NULL, 'lavka', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
  ,(
        'euid-3', 'eda', 1, 2,
        'ya1', '12525', 'created', '35,64',
        '23523', '0', '2523sdsdga sdg asdgdg', '2020-06-15T09:00:00Z',
        NULL, 'native', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
  ,(
        'euid-4', 'lavka', 1, 2,
        NULL, '12525', 'created', '35,64',
        '23523', '0', '2523sdsdga sdg asdgdg', '2020-06-14T08:00:00Z',
        NULL, 'lavka', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
  ,(
        'euid-5', 'lavka', 1, 2,
        NULL, '12525', 'taken', '35,64',
        '23523', '0', '2523sdsdga sdg asdgdg', '2020-06-14T07:00:00Z',
        NULL, 'lavka', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
  ,(
        'euid-6', 'lavka', 1, 2,
        NULL, '12525', 'taken', '35,64',
        '23523', '0', '2523sdsdga sdg asdgdg', '2020-06-13T07:00:00Z',
        NULL, 'lavka', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
  ,(
        'euid-7', 'lavka', 1, 2,
        NULL, '12525', 'taken', '35,64',
        '23523', '0', '2523sdsdga sdg asdgdg', '2020-06-01T11:00:00Z',
        NULL, 'lavka', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
  ,(
        'euid-8', 'lavka', 3, 4,
        'ya3', '123', 'taken', '5.67,4.56',
        '45', '0', 'any reason', '2020-05-06T21:48:44.747Z',
        '2020-05-06T22:24:21.747Z', 'lavka', '100.00', 'RUB', 'delivery',
        'native', '2020-06-15T11:00:00Z', NULL, NULL
    )
  ,(
        'order-uid-1', 'eda', 1234, 4,
        'uid-1', '123', 'taken', '5.67,4.56',
        '45', '0', 'any reason', '2020-05-06T21:48:00Z',
        NULL, 'native', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
  ,(
        'order-uid-2', 'lavka', 1234, 4,
        NULL, '123', 'taken', '5.67,4.56',
        '45', '0', 'any reason', '2020-05-06T21:49:00Z',
        NULL, 'lavka', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
  ,(
        'order-uid-3', 'eda', 12345, 4,
        'uid-2', '123', 'taken', '5.67,4.56',
        '45', '0', 'any reason', '2020-05-06T21:50:00Z',
        NULL, 'native', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
  ,(
        'order-uid-4', 'eda', 12345, 4,
        NULL, '123', 'taken', '5.67,4.56',
        '45', '0', 'any reason', '2020-05-06T21:51:00Z',
        NULL, 'native', '100.00', 'RUB', 'delivery', 'native', NULL, NULL, NULL
    )
;


INSERT INTO eats_ordershistory.cart_items (
    "order_id", "place_menu_item_id", "name", "quantity", "origin_id", "catalog_type"
)
VALUES
    ('euid-1', '235', 'sddsgas', '24', '235', 'core_catalog')
   ,('euid-2', '235', 'sddsgas', '24', '235', 'core_catalog')
   ,('euid-3', '235', 'sddsgas', '24', '235', 'core_catalog')
   ,('euid-8', '3', 'title-1', '4', '3', 'core_catalog')
   ,('euid-8', '5', 'title-2', '8', '5', 'core_catalog')
;

INSERT INTO eats_ordershistory.feedbacks (
    "order_id", "rating", "comment"
)
VALUES
    ('euid-1', NULL, NULL)
   ,('euid-2', NULL, NULL)
;

INSERT INTO eats_ordershistory.addresses (
    "order_id", "full_address", "entrance", "floor_number",
    "office", "doorcode", "comment"
)
VALUES
    ('euid-1', 'address1', '2', '4', '13', '34452', 'comment1')
   ,('euid-2', 'address2', NULL, '4', '13', NULL, 'comment2')
   ,('euid-3', 'address3', NULL, NULL, NULL, NULL, NULL)
   ,('euid-4', 'address4', '56', NULL, '19', '45', NULL)
   ,('euid-5', NULL, NULL, NULL, NULL, NULL, NULL)
   ,('euid-6', 'address5', '83', '12', '13', '1332', 'comment5')
   ,('euid-7', 'address6', NULL, NULL, NULL, NULL, 'comment6')
   ,('euid-8', 'address7', '29', '43', '83', '12', 'comment7')
   ,('order-uid-1', NULL, NULL, NULL, NULL, NULL, 'comment8')
   ,('order-uid-2', NULL, NULL, NULL, NULL, NULL, NULL)
   ,('order-uid-3', 'address9', '3429', '4', '483', '122', 'comment9')
   ,('order-uid-4', 'address10', NULL, '43', NULL, '12', NULL)
;

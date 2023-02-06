UPSERT INTO `orders_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
(
    "order_1",
    "order.user_id",
    '\x1d\x00\x00\x00\x02data\x00\x0e\x00\x00\x00original_user\x00\x00',
    '\x19\x00\x00\x00\x02data\x00\n\x00\x00\x00fake_user\x00\x00',
    True
);
UPSERT INTO `orders_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
(
    "order_1",
    "order.field1",
    '\x1f\x00\x00\x00\x02data\x00\x10\x00\x00\x00field1_original\x00\x00',
    '\x10\x00\x00\x00\x03data\x00\x05\x00\x00\x00\x00\x00',
    True
);
UPSERT INTO `orders_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
(
    "order_1",
    "foo",
    '\x1c\x00\x00\x00\x02data\x00\r\x00\x00\x00bar_original\x00\x00',
    '\x10\x00\x00\x00\x03data\x00\x05\x00\x00\x00\x00\x00',
    True
);
UPSERT INTO `orders_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
(
    "order_1",
    "candidates.1.name",
    '\x14\x00\x00\x00\x02data\x00\x05\x00\x00\x00FIO2\x00\x00',
    '\x10\x00\x00\x00\x03data\x00\x05\x00\x00\x00\x00\x00',
    True
);
UPSERT INTO `orders_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
(
    "order_1",
    "candidates.2.name",
    '\x14\x00\x00\x00\x02data\x00\x05\x00\x00\x00FIO3\x00\x00',
    '\x10\x00\x00\x00\x03data\x00\x05\x00\x00\x00\x00\x00',
    True
);
UPSERT INTO `orders_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
("order_1", "not_commited", '', '', False);
UPSERT INTO `orders_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
("order_extra", "extra_order", '', '', True);

UPSERT INTO `orders_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
(
    "order_2",
    "order.users.0.foo.0.bar.value",
    '\x0f\x00\x00\x00\x10data\x00\x0b\x00\x00\x00\x00',
    '\x10\x00\x00\x00\x03data\x00\x05\x00\x00\x00\x00\x00',
    True
);
UPSERT INTO `orders_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
(
    "order_2",
    "order.users.1.foo.0.bar.value",
    '\x0f\x00\x00\x00\x10data\x00\x16\x00\x00\x00\x00',
    '\x10\x00\x00\x00\x03data\x00\x05\x00\x00\x00\x00\x00',
    True
);
UPSERT INTO `orders_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
(
    "order_2",
    "order.users.0.foo.1.bar2",
    '/\x00\x00\x00\x03data\x00$\x00\x00\x00\x04abc\x00\x1a\x00\x00\x00\x100\x00\x01\x00\x00\x00\x101\x00\x02\x00\x00\x00\x102\x00\x03\x00\x00\x00\x00\x00\x00',
    '\x10\x00\x00\x00\x03data\x00\x05\x00\x00\x00\x00\x00',
    True
);

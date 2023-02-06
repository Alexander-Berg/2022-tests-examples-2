UPSERT INTO `order_proc_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
("order_1", "order.user_id", '\x1d\x00\x00\x00\x02data\x00\x0e\x00\x00\x00original_user\x00\x00', '\x19\x00\x00\x00\x02data\x00\n\x00\x00\x00fake_user\x00\x00', True);
UPSERT INTO `order_proc_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
("order_1", "candidates.0.driver", '-\x00\x00\x00\x03data\x00"\x00\x00\x00\x03driver\x00\x15\x00\x00\x00\x07id\x00^\x00\xb6a\x95M\xe7M\x8aj\xf7\xc7\x00\x00\x00', '\x10\x00\x00\x00\x03data\x00\x05\x00\x00\x00\x00\x00', True);
UPSERT INTO `order_proc_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
("order_1", "not_commited", '', '', False);
UPSERT INTO `order_proc_fields` (order_id, json_path, original_value, anonymized_value, committed) VALUES
("order_extra", "extra_order", '', '', True);

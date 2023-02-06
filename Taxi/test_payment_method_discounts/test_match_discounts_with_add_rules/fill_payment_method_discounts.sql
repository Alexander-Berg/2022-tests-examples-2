INSERT INTO menu_grocery_discounts.groups (field_type, field_value)
VALUES ('Type', 'food');

INSERT INTO menu_grocery_discounts.groups_priority (group_id, priority)
VALUES (1, 1);

INSERT INTO grocery_discounts.bin_sets(id, bin_set_name, bins, from_ts, to_ts)
VALUES
(511, 'SuperGroup', '{123321, 405060}', '2020-01-01 05:00:00.000+03', '2020-07-18 10:00:00.000+03'),
(411, 'AlphaBank', '{444444, 555555}', '2020-01-01 05:00:00.000+03', '2020-08-12 10:00:00.000+03');

INSERT INTO grocery_discounts.bins_priority (bin_set_id, priority)
VALUES
(511, 1),
(411, 2);

BEGIN TRANSACTION;

SET CONSTRAINTS ALL DEFERRED;

INSERT INTO grocery_discounts.bin_sets(id, bin_set_name, bins, from_ts, to_ts)
VALUES
(511, 'Любимое', '{123321, 234432}', '2020-07-11 05:00:00.000+03', '2020-07-18 10:00:00.000+03'),
(411, 'Кофеманы', '{444444, 555555}', '2020-08-11 05:00:00.000+03', '2020-08-12 10:00:00.000+03'),
(311, 'Прошла', '{213321, 123333}', '2020-06-11 05:00:00.000+03', '2020-06-12 10:00:00.000+03'),
(211, 'Красивые', '{666666, 777777}', '2020-07-11 05:00:00.000+03', '2020-07-22 10:00:00.000+03');

INSERT INTO grocery_discounts.bins_priority (bin_set_id, priority)
VALUES
(511, 1),
(211, 2);

COMMIT TRANSACTION;

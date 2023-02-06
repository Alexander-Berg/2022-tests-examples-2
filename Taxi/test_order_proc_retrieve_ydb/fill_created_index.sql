UPSERT INTO `order_proc/indexes/order_proc_created_index` (id, created, partition) VALUES
("id1", CAST(DateTime::FromSeconds(1646845023) AS datetime), "2022-03"),
("id2", CAST(DateTime::FromSeconds(1646845023) AS datetime), "2022-03"),
("id3", CAST(DateTime::FromSeconds(1646845023) AS datetime), "2022-03")

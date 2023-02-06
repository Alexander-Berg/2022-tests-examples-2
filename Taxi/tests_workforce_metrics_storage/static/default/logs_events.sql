INSERT INTO events.logs_64_partitioned_11_mod_30 (
  event_id,
  employee_id,
  event_type_id,
  descriptor,
  extra_data,
  created,
  deadline,
  processed
) VALUES
	(100, 1001,1,'{"name":"proc"}','{}','2000-01-01T00:00:01','2100-01-01T00:00:00','2000-01-01T00:01:01'),
	(101, 1001,1,'{"name":"info"}','{}','2000-01-01T00:00:02','2100-01-01T00:00:00','2000-01-01T00:01:02');

INSERT INTO events.logs_64_partitioned_12_mod_30 (
  event_id,
  employee_id,
  event_type_id,
  descriptor,
  extra_data,
  created,
  deadline,
  processed
) VALUES
	(102, 1002,1,'{"name":"proc"}','{}','2000-01-01T00:00:03','2100-01-01T00:00:00','2000-01-01T00:01:03'),
	(103, 1002,1,'{"name":"info"}','{}','2000-01-01T00:00:04','2100-01-01T00:00:00','2000-01-01T00:01:04');

INSERT INTO events.logs_64_partitioned_13_mod_30 (
  event_id,
  employee_id,
  event_type_id,
  descriptor,
  extra_data,
  created,
  deadline,
  processed
) VALUES
	(104, 1003,1,'{"name":"proc"}','{}','2000-01-01T00:00:05','2100-01-01T00:00:00','2000-01-01T00:01:05'),
	(105, 1003,1,'{"name":"info"}','{}','2000-01-01T00:00:06','2100-01-01T00:00:00','2000-01-01T00:01:06');


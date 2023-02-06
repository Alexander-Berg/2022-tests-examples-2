INSERT INTO chatterbox_deliveries.waiting_task_deliveries (id, created_ts)
OVERRIDING SYSTEM VALUE
VALUES (1, '2021-09-20 17:00:00.000000+00');


INSERT INTO chatterbox_tasks.waiting_tasks
  (id, login, line, status, waiting_time, updated_ts, delivery_id)
VALUES
  ('task_1', '', 'first', 'offered', 180, '2021-09-20 17:00:13.000000+00', 1),
  ('task_2', 'support_1', 'first', 'accepted', 60, '2021-09-20 17:00:49.000000+00', 1),
  ('task_3', '', '', 'new', 420, '2021-09-20 17:01:15.000000+00', 1),
  ('task_4', 'support_2', 'second', 'in_progress', 300, '2021-09-20 17:01:54.000000+00', 1),
  ('task_5', '', 'second', 'reopened', 300, '2021-09-20 17:02:24.000000+00', 1),
  ('task_6', '', 'second', 'forwarded', 720, '2021-09-20 17:03:00.000000+00', 1);

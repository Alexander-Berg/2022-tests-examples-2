INSERT INTO chatterbox_deliveries.waiting_task_deliveries (id, created_ts)
OVERRIDING SYSTEM VALUE
VALUES
    (1, '2021-09-30 16:17:56.000000+00'),
    (2, '2021-10-01 16:17:56.000000+00'),
    (3, '2021-10-02 16:17:56.000000+00');


INSERT INTO chatterbox_tasks.waiting_tasks
  (id, login, line, status, waiting_time, delivery_id)
VALUES
  ('task_1', '', '', 'new', 60, 1),
  ('task_1', 'support_1', 'first', 'in_progress', 120, 2),
  ('task_2', 'support_2', 'second', 'accepted', 10, 2),
  ('task_2', 'support_2', 'second', 'in_progress', 40, 3),
  ('task_3', '', '', 'forwarded', 180, 3),
  ('task_4', 'support_3', 'vip', 'in_progress', 5, 3);

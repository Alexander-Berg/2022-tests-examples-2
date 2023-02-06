INSERT INTO chatterbox_deliveries.waiting_task_deliveries (id, created_ts)
OVERRIDING SYSTEM VALUE
VALUES (1, '2021-10-02 16:17:56.000000+00');


INSERT INTO chatterbox_tasks.waiting_tasks
  (id, login, line, status, waiting_time, updated_ts, delivery_id)
VALUES
  ('task_1', '', '', 'new', 60, '2021-10-02 16:18:10.000000+00', 1),
  ('task_2', 'support_1', 'first', 'in_progress', 120, '2021-10-02 16:18:39.000000+00', 1);

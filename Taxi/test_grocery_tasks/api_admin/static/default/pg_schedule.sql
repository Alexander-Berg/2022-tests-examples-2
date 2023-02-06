INSERT INTO grocery_tasks.schedule
    (task_name, cron_schedule, next_run)
VALUES
    ('autoorder-run_data_copy', '3 4 * * *', null),
    ('autoorder-run_calc', '3 7 * * *', '2020-04-15T07:00:00+03:00'),
    ('selloncogs-update_experiment', '5 7 * * *', '2020-04-15T07:00:00+03:00');

INSERT INTO grocery_tasks.history
    (task_id, task_name, start_at, end_at, status, report_short)
VALUES
    ('99', 'autoorder-run_data_copy', '2019-04-14T07:03:00+03:00', '2019-04-14T07:05:00+03:00', 'ok', null),
    ('100', 'autoorder-run_data_copy', '2020-04-13T07:03:00+03:00', '2020-04-14T07:04:00+03:00', 'ok', 'abc'),
    ('101', 'autoorder-run_data_copy', '2020-04-14T07:03:00+03:00', '2020-04-14T07:04:00+03:00', 'ok', null),
    ('200', 'autoorder-run_calc', '2020-04-14T07:04:00+03:00', '2020-04-14T07:05:00+03:00', 'warning', null),
    ('300', 'selloncogs-update_experiment', '2020-04-14T07:05:00+03:00', '2020-04-14T07:06:00+03:00', 'ok', null);

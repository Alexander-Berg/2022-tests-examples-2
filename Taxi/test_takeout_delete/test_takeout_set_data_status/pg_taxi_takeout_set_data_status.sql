INSERT INTO takeout.deletions (yandex_uid, data_category, status, service_name, deleted_at, status_updated_at, last_deletion_request_at)
VALUES ('12345', 'grocery', 'deleted', 'grocery-service', CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ), CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ), CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ)),
       ('12345', 'eats', 'deleting', 'takeout', null, CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ), CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ)),
       ('12346', 'grocery', 'deleted', 'grocery-service', CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ), CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ), CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ)),
       ('12345', 'taxi', 'deleting', 'user-api', null, CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ), CAST('2018-01-01 10:00:00' AS TIMESTAMPTZ))
;

INSERT INTO cursors
    (id, name, last_id, last_updated_at)
VALUES
    (0, 'user_login_attempt_statistics', 0, '2021-08-17 13:15:14');


INSERT INTO user_login_attempt
    (id, msisdn, token, sms_code, status_name, updated_at)
VALUES
    (0, 11110, 11110, 1110, 'REJECTED_FLOODING_FILTER', '2021-08-17 13:15:14'), -- too old
    (1, 11111, 11111, 1111, 'REJECTED_FLOODING_FILTER', '2021-08-17 13:23:14'),
    (2, 11112, 11112, 1112, 'REJECTED_FLOODING_FILTER', '2021-08-17 13:23:14'),
    (3, 11113, 11113, 1113, 'REJECTED_FLOODING_FILTER', '2021-08-17 13:23:14'),
    (4, 11114, 11114, 1114, 'FAILED_TO_FETCH_STATUS', '2021-08-17 13:23:14'),
    (5, 11115, 11115, 1115, 'DELIVERED_TO_HANDSET', '2021-08-17 13:24:14'),
    (6, 11116, 11116, 1116, 'DELIVERED_TO_HANDSET', '2021-08-17 13:25:14');

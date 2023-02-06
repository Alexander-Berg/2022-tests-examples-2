DROP TRIGGER set_updated ON sticker.mail_queue;

INSERT INTO sticker.mail_queue
    (id, body, idempotence_token, recipient, status, created, updated, run_id, via_sender)
VALUES (
    0, '', '1', 'id1', 'PENDING',
    CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP), CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP),
    'run_id_1', FALSE
),
(
    1, '', '2', 'id1', 'PROCESSING',
    CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP), CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP),
    'run_id_2', FALSE
),
(
    2, '', '3', 'id1', 'PROCESSING',
    CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP), CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP),
    'run_id_1', FALSE
),
(
    3, '', '4', 'id1', 'PROCESSING',
    CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP), CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP),
    'run_id_1', FALSE
),
(
    4, '', '5', 'id1', 'PENDING',
    CAST('2021-02-18 13:59:00.000000' AS TIMESTAMP), CAST('2021-02-18 14:00:00.000000' AS TIMESTAMP),
    'run_id_1', TRUE
),
(
    5, '', '6', 'id1', 'PENDING',
    CAST('2021-02-18 14:00:00.000000' AS TIMESTAMP), CAST('2021-02-18 14:00:00.000000' AS TIMESTAMP),
    'run_id_1', TRUE
),
(
    6, '', '7', 'id1', 'PENDING',
    CAST('2021-02-18 14:06:00.000000' AS TIMESTAMP), CAST('2021-02-18 14:06:00.000000' AS TIMESTAMP),
    'run_id_1', TRUE
),
(
    7, '', '8', 'id1', 'PROCESSING',
    CAST('2021-02-18 14:00:00.000000' AS TIMESTAMP), CAST('2021-02-18 14:00:00.000000' AS TIMESTAMP),
    'run_id_1', TRUE
);

CREATE TRIGGER set_updated BEFORE UPDATE OR INSERT ON sticker.mail_queue
FOR EACH ROW EXECUTE PROCEDURE set_updated();

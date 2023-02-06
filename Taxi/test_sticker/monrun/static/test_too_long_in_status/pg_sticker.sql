DROP TRIGGER set_updated ON sticker.mail_queue;

-- Now is '2019-01-02 09:00:00.000000'

INSERT INTO sticker.mail_queue (id, body, idempotence_token, recipient, status, updated, send_after) VALUES
(
    11, '<mails><mail><from>a@a.a</from></mail></mails>', '4', 'id01', 'PENDING',
    CAST('2019-01-02 08:32:28.936361' AS TIMESTAMP),
    CAST('2019-01-02 08:32:28.936361' AS TIMESTAMP)
),
(
    12, '<mails><mail><from>a@a.a</from></mail></mails>', '5', 'id01', 'PENDING',
    CAST('2019-01-02 08:01:28.936361' AS TIMESTAMP),
    CAST('2019-01-02 08:01:28.936361' AS TIMESTAMP)
),
(
    14, '<mails><mail><from>a@a.a</from></mail></mails>', '8', 'id01', 'PROCESSING',
    CAST('2019-01-02 08:59:28.936361' AS TIMESTAMP),
    CAST('2019-01-02 08:59:28.936361' AS TIMESTAMP)
),
(
    15, '<mails><mail><from>a@a.a</from></mail></mails>', '9', 'id01', 'PROCESSING',
    CAST('2019-01-02 07:01:28.936361' AS TIMESTAMP),
    CAST('2019-01-02 07:01:28.936361' AS TIMESTAMP)
),
(
    16, '<mails><mail><from>a@a.a</from></mail></mails>', '10', 'id01', 'PROCESSING',
    CAST('2019-01-02 07:41:28.936361' AS TIMESTAMP),
    CAST('2019-01-02 07:41:28.936361' AS TIMESTAMP)
);

CREATE TRIGGER set_updated BEFORE UPDATE OR INSERT ON sticker.mail_queue
FOR EACH ROW EXECUTE PROCEDURE set_updated();

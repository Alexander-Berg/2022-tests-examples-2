DROP TRIGGER set_updated ON sticker.mail_queue;

-- Now is '2019-01-02 09:00:00.000000'

INSERT INTO sticker.mail_queue (id, body, idempotence_token, recipient, status, updated, send_after) VALUES
(
    1, '<mails><mail><from>a@a.a</from></mail></mails>', '1', 'id01', 'PENDING',
    CAST('2019-12-04 07:00:00' AS TIMESTAMP),
    CAST('2019-12-04 07:00:00' AS TIMESTAMP)
),
(
    2, '<mails><mail><from>a@a.a</from></mail></mails>', '2', 'id01', 'PENDING',
    CAST('2019-12-04 07:00:00' AS TIMESTAMP),
    CAST('2019-12-04 07:12:00' AS TIMESTAMP)
);

CREATE TRIGGER set_updated BEFORE UPDATE OR INSERT ON sticker.mail_queue
FOR EACH ROW EXECUTE PROCEDURE set_updated();

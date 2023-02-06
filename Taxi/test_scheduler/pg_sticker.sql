DROP TRIGGER set_updated ON sticker.mail_queue;

INSERT INTO sticker.mail_queue
    (id, body, idempotence_token, recipient, status, created, updated)
VALUES
    (1, '<mails><mail><from>a@a.a</from></mail></mails>', '1', 'id1', 'PENDING',
     CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP), CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP));

INSERT INTO sticker.mail_queue
    (id, body, idempotence_token, recipient, recipient_type, status, created, updated)
VALUES
    (2, '<mails><mail><from>a@a.a</from></mail></mails>', '2', 'ya@ya.ru', 'INTERNAL', 'PENDING',
     CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP), CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP));

CREATE TRIGGER set_updated BEFORE UPDATE OR INSERT ON sticker.mail_queue
FOR EACH ROW EXECUTE PROCEDURE set_updated();

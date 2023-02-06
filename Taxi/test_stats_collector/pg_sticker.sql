DROP TRIGGER set_updated ON sticker.mail_queue;

INSERT INTO sticker.mail_queue (id, body, idempotence_token, recipient, status, created, updated) VALUES
  (11, '<mails><mail><from>a@a.a</from></mail></mails>', '1', 'id01', 'PENDING',
   (NOW() AT TIME ZONE 'UTC')::TIMESTAMP - INTERVAL '1 second',
   CAST('2019-01-02 08:40:28.936361' AS TIMESTAMP));

CREATE TRIGGER set_updated BEFORE UPDATE OR INSERT ON sticker.mail_queue
FOR EACH ROW EXECUTE PROCEDURE set_updated();

DROP TRIGGER set_updated ON sticker.mail_queue;

INSERT INTO sticker.mail_queue (id, body, idempotence_token, recipient, status, created, updated) VALUES
  (11, '<mails><mail><from>a@a.a</from></mail></mails>', '1', 'id01', 'SCHEDULED',
   CAST('2019-01-02 07:39:28.936361' AS TIMESTAMP), CAST('2019-01-02 08:39:28.936361' AS TIMESTAMP)),
  (12, '<mails><mail><from>a@a.a</from></mail></mails>', '2', 'id01', 'SCHEDULED',
   CAST('2019-01-01 06:00:28.936361' AS TIMESTAMP), CAST('2019-01-01 07:00:28.936361' AS TIMESTAMP)),
  (13, '<mails><mail><from>a@a.a</from></mail></mails>', '3', 'id01', 'SCHEDULED',
   CAST('2019-01-02 06:00:28.936361' AS TIMESTAMP), CAST('2019-01-02 07:00:28.936361' AS TIMESTAMP)),

  (14, '<mails><mail><from>a@a.a</from></mail></mails>', '4', 'id01', 'PENDING',
   CAST('2019-01-02 06:59:28.936361' AS TIMESTAMP), CAST('2019-01-02 06:59:28.936361' AS TIMESTAMP)),
  (15, '<mails><mail><from>a@a.a</from></mail></mails>', '5', 'id01', 'PENDING',
   CAST('2019-01-02 07:01:28.936361' AS TIMESTAMP), CAST('2019-01-02 07:01:28.936361' AS TIMESTAMP)),

  (16, '<mails><mail><from>a@a.a</from></mail></mails>', '6', 'id01', 'TO_RETRY',
   CAST('2019-01-02 04:59:28.936361' AS TIMESTAMP), CAST('2019-01-02 06:59:28.936361' AS TIMESTAMP)),
  (17, '<mails><mail><from>a@a.a</from></mail></mails>', '7', 'id01', 'TO_RETRY',
   CAST('2019-01-02 07:01:28.936361' AS TIMESTAMP), CAST('2019-01-02 07:01:28.936361' AS TIMESTAMP)),

  (18, '<mails><mail><from>a@a.a</from></mail></mails>', '8', 'id01', 'PROCESSING',
   CAST('2019-01-02 06:59:28.936361' AS TIMESTAMP), CAST('2019-01-02 08:59:28.936361' AS TIMESTAMP)),
  (19, '<mails><mail><from>a@a.a</from></mail></mails>', '9', 'id01', 'PROCESSING',
   CAST('2019-01-02 07:01:28.936361' AS TIMESTAMP), CAST('2019-01-02 07:01:28.936361' AS TIMESTAMP)),

  (20, '<mails><mail><from>a@a.a</from></mail></mails>', '10', 'id01', 'FAILED',
   CAST('2019-01-02 04:59:28.936361' AS TIMESTAMP), CAST('2019-01-02 06:59:28.936361' AS TIMESTAMP)),
  (21, '<mails><mail><from>a@a.a</from></mail></mails>', '11', 'id01', 'FAILED',
   CAST('2019-01-02 07:01:28.936361' AS TIMESTAMP), CAST('2019-01-02 07:01:28.936361' AS TIMESTAMP));

CREATE TRIGGER set_updated BEFORE UPDATE OR INSERT ON sticker.mail_queue
FOR EACH ROW EXECUTE PROCEDURE set_updated();

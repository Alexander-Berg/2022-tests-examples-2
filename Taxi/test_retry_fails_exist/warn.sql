INSERT INTO sticker.mail_queue (id, body, idempotence_token, recipient, status, fail_count) VALUES
  (1001, '<mails><mail><from>a@a.a</from></mail></mails>', '1', 'id01', 'TO_RETRY', 2),
  (1002, '<mails><mail><from>a@a.a</from></mail></mails>', '2', 'id01', 'FAILED', 0),
  (1003, '<mails><mail><from>a@a.a</from></mail></mails>', '3', 'id01', 'PROCESSING', 0),
  (1004, '<mails><mail><from>a@a.a</from></mail></mails>', '4', 'id01', 'SCHEDULED', 0),
  (1005, '<mails><mail><from>a@a.a</from></mail></mails>', '5', 'id01', 'TO_RETRY', 0);

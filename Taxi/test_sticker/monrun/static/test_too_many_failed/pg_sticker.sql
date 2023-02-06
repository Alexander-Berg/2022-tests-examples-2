INSERT INTO sticker.mail_queue (id, body, idempotence_token, recipient, status, via_sender) VALUES
  (1000, '<mails><mail><from>a@a.a</from></mail></mails>', '1', 'id01', 'FAILED', TRUE),
  (1001, '<mails><mail><from>a@a.a</from></mail></mails>', '2', 'id01', 'FAILED', FALSE),
  (1002, '<mails><mail><from>a@a.a</from></mail></mails>', '3', 'id01', 'FAILED', FALSE),
  (1003, '<mails><mail><from>a@a.a</from></mail></mails>', '4', 'id01', 'FAILED', FALSE),
  (1004, '<mails><mail><from>a@a.a</from></mail></mails>', '5', 'id01', 'PROCESSING', FALSE),
  (1005, '<mails><mail><from>a@a.a</from></mail></mails>', '6', 'id01', 'SCHEDULED', FALSE),
  (1006, '<mails><mail><from>a@a.a</from></mail></mails>', '7', 'id01', 'TO_RETRY', FALSE);

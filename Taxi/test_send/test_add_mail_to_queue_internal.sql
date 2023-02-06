INSERT INTO sticker.mail_queue (id, body, idempotence_token, recipient, recipient_type, status) VALUES
  (1001, '<mails><mail><from>a@a.a</from></mail></mails>', '1', 'someone@yandex-team.ru', 'INTERNAL', 'PENDING'),
  (1002, '<mails><mail><from>a@a.a</from></mail></mails>', '2', 'someone@yandex-team.ru', 'INTERNAL', 'PROCESSING'),
  (1003, '<mails><mail><from>a@a.a</from></mail></mails>', '3', 'someone@yandex-team.ru', 'INTERNAL', 'TO_RETRY'),
  (1004, '<mails><mail><from>a@a.a</from></mail></mails>', '4', 'someone@yandex-team.ru', 'INTERNAL', 'FAILED'),
  (1005, '<mails><mail><from>a@a.a</from></mail></mails>', '5', 'someone@yandex-team.ru', 'INTERNAL', 'SCHEDULED');

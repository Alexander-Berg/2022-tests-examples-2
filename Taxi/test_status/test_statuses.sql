INSERT INTO sticker.mail_queue
(id, body,
 idempotence_token, recipient, status)
VALUES
       (1001, '<mails><mail><from>a@a.a</from></mail></mails>',
        '1', '1', 'PENDING'),
        (1002, '<mails><mail><from>a@a.a</from></mail></mails>',
        '2', '2', 'PROCESSING'),
        (1003, '<mails><mail><from>a@a.a</from></mail></mails>',
        '3', '3', 'TO_RETRY'),
        (1004, '<mails><mail><from>a@a.a</from></mail></mails>',
        '4', '4', 'FAILED'),
        (1005, '<mails><mail><from>a@a.a</from></mail></mails>',
        '5', '5', 'SCHEDULED');


INSERT INTO sticker.mail_queue
    (id, body, idempotence_token, recipient, recipient_type, status)
VALUES
    (1, '<mails><mail><from>a@a.a</from></mail></mails>', '1', 'ya@ya.ru', 'INTERNAL', 'PENDING');

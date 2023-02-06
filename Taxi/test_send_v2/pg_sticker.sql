INSERT INTO sticker.mail_queue (
    body, idempotence_token, recipient, status, via_sender, tvm_name
)
VALUES ('',  '1', '1', 'SCHEDULED', TRUE, 'tvm_old_service');

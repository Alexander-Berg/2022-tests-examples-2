INSERT
INTO eats_receipts.send_receipt_requests(id,
                                         document_id,
                                         is_refund,
                                         order_id,
                                         order_info.country_code,
                                         order_info.payment_method,
                                         user_info.personal_email_id,
                                         originator,
                                         request,
                                         status)
VALUES (1, 'doc/what/is/up', False, '1', '000', 'card'::eats_receipts.payment_method, '1', 'test_originator', '{}',
        'created'),
       (2, '12', False, '1', '000', 'card'::eats_receipts.payment_method, '1', 'originaror', '{}', 'created'),
       (3, '332', False, '1', '000', 'card'::eats_receipts.payment_method, '1', 'originaror', '{}', 'created'),
       (4, '335', False, '1', '000', 'card'::eats_receipts.payment_method, '1', 'originaror', '{}', 'created')
;

INSERT
INTO eats_receipts.send_receipt_ofd_info(id,
                                         status,
                                         device_rn,
                                         document_number,
                                         fiscal_sign,
                                         ofd_name,
                                         request_id,
                                         document_id,
                                         originator, created_at)
VALUES (11, 'pending', 'XXXXXXXXXXXXXXXX', '1', 'Яндекс.ОФД', 'XXXXXXXXXXXXXXXX', 1, 'doc/what/is/up',
        'test_originator', NOW()),
       (12, 'failed', 'XXXXXXXXXXXXXXXX', '1', 'Яндекс.ОФД', 'XXXXXXXXXXXXXXXX', 2, '12', 'originaror', NOW()),
       (13, 'pending', 'XXXXXXXXXXXXXXXX', '1', 'Яндекс.ОФД', 'XXXXXXXXXXXXXXXX', 3, '332', 'originaror', NOW()),
       (14, 'pending', 'XXXXXXXXXXXXXXXX', '1', 'Яндекс.ОФД', 'XXXXXXXXXXXXXXXX', 4, '335', 'originaror', NOW() - INTERVAL '6 DAY')
;

INSERT INTO eats_receipts.send_receipt_payture_info(id,
                                                    document_id,
                                                    originator,
                                                    status)
VALUES ('1', 'doc/what/is/up', 'test_originator', 'failed'),
       ('2', '1', 'originator', 'failed')
;

INSERT INTO
    eats_receipts.stq_failed_tasks(order_id, failed_stq_name, created_at, failed_at, fixed_at, error_message,
                                   stq_arguments)
VALUES
    ('1', 'eats_send_receipt_ofd_check', NOW(), NOW(), NULL, 'bad stuff', '{"request_id":1}');

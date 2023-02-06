INSERT INTO eats_receipts.stq_failed_tasks(order_id, failed_stq_name, created_at, failed_at, fixed_at, error_message,
                                           stq_arguments)
VALUES (1, 'eats_send_receipt_payture_check', NOW(), NOW(), NULL, 'bad stuff', 'arg: yes'),
       (2, 'eats_send_receipt_payture_check', NOW(), NOW(), NOW(), 'bad stuff', 'arg: yes'),
       (3, 'eats_send_receipt_ofd_check', NOW(), NOW(), NULL, 'other bad stuff', 'arg: why'),
       (3, 'eats_send_receipt_ofd_check', NOW(), NOW(), NULL, 'bad stuff', 'arg: yes');

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
                                         status,
                                         created_at,
                                         updated_at)
VALUES (1, 'doc/what/is/up', False, '1', '000', 'card'::eats_receipts.payment_method, '1', 'test_originator', '{}',
        'created', NOW()-interval '5 MINUTE', NOW()-interval '5 MINUTE'),
       (2, '12', False, '1', '000', 'card'::eats_receipts.payment_method, '1', 'originaror', '{}', 'created',
        NOW()-interval '7 MINUTE', NOW()-interval '7 MINUTE')
;



INSERT
INTO eats_receipts.receipts_info(id, document_id, receipt_type, info, originator, order_id, created_at, updated_at)
VALUES (1, 'doc/what/is/up', 'goods', '1', 'test_originator', '1', NOW(), NOW()),
       (2, '12', 'refund', '1', 'originaror', '1', NOW() - interval '4 MINUTE', NOW() - interval '4 MINUTE')
;

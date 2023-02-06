INSERT INTO eats_receipts.send_receipt_requests(id,
                                                order_id,
                                                is_refund,
                                                document_id,
                                                order_info.country_code,
                                                order_info.payment_method,
                                                originator,
                                                user_info.personal_email_id,
                                                request)
VALUES ('0', '123456-123456', false, '0', '000', 'card'::eats_receipts.payment_method, 'originator', 'aser@dgq.tu',
        '{}'),
       ('1', '123456-123456', false, '1', '000', 'card'::eats_receipts.payment_method, 'originator', 'aser@dgq.tu',
        '{}'),
       ('2', '123456-123456', false, '2', '000', 'card'::eats_receipts.payment_method, 'another_originator', 'aser@dgq.tu',
        '{}');

INSERT INTO eats_receipts.receipts_info(id,
                                        order_id,
                                        document_id,
                                        originator,
                                        receipt_type,
                                        info)
VALUES ('1', '123456-123456', '0', 'originator', 'YandexOFD',
        '{"fiscalDocumentNumber": 11111,"fiscalSign": 22222,"ofd_name": "ddddd","kktRegId": "ffffff1"}'),
       ('2', '123456-123456', '1', 'originator', 'YandexOFD',
        '{"fiscalDocumentNumber": 11111,"fiscalSign": 33333,"ofd_name": "ddddd","kktRegId": "ffffff2"}'),
       ('3', '123456-123456', '2', 'another_originator', 'YandexOFD',
        '{"fiscalDocumentNumber": 11111,"fiscalSign": 44444,"ofd_name": "ddddd","kktRegId": "ffffff3"}');

INSERT INTO eats_receipts.send_receipt_payture_info(
    id,
    document_id,
    status,
    originator,
    cheque_id
) VALUES
      ('1', '0', 'success', 'originator', 'cheque_id'),
      ('2', '1', 'success', 'originator', 'cheque_id'),
      ('3', '2', 'success', 'originator', 'cheque_id')

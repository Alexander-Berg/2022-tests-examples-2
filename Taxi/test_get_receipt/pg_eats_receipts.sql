INSERT INTO eats_receipts.send_receipt_requests(
        id,
        order_id,
        is_refund,
        document_id,
        order_info.country_code,
        order_info.payment_method,
        originator,
        user_info.personal_email_id,
        request)
        VALUES
               ('1', '1', false, '0', '000', 'card'::eats_receipts.payment_method, 'originator', 'aser@dgq.tu', '{}'),
               ('2', '2', false, '1', '111', 'card'::eats_receipts.payment_method, 'originator', 'aser@dgq.tu', '{}');

INSERT INTO eats_receipts.receipts_info(
    id,
    order_id,
    document_id,
    originator,
    receipt_type,
    info,
    sum)
VALUES
    ('1', '1', '0', 'originator', 'YandexOFD', '{"fiscalDocumentNumber": 11111,"fiscalSign": 22222,"ofd_name": "ddddd","kktRegId": "ffffff"}', NULL),
    ('2', '2', '1', 'originator', 'YandexOFD', '{"fiscalDocumentNumber": 11111,"fiscalSign": 22222,"ofd_name": "ddddd","kktRegId": "ffffff"}', '123.45');

INSERT INTO eats_receipts.send_receipt_payture_info(
    id,
    document_id,
    status,
    originator,
    cheque_id
) VALUES
    ('1', '0', 'success', 'originator', 'cheque_id'),
    ('2', '1', 'success', 'originator', 'cheque_id');

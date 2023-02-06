INSERT INTO payment_transactions (uuid, order_id, order_items, payment_type, front_uuid, side_payment_id, status)
VALUES ('transaction_uuid__1',
        1,
        '[{"id": "product_id__1", "title": "Торт с холестерином", "price": 0.1,
        "base_price": 0.1, "quantity": 1, "in_pay_count": 0, "paid_count": 0,
        "vat": 20.0},
           {"id" : "product_id__2", "title": "Палтус за палтус", "price": 0.2,
        "base_price": 0.2, "quantity": 1, "in_pay_count": 0, "paid_count": 0,
        "vat": 20.0}]',
        'payture',
        'transaction_front_uuid__1',
        1,
        'in_progress')
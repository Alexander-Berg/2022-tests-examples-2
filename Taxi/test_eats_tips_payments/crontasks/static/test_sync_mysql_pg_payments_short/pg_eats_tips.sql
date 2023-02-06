INSERT INTO eats_tips_payments.orders (
    id,
    order_id,
    amount,
    yandex_user_id,
    user_ip,
    user_has_plus,
    plus_amount,
    cashback_status,
    is_refunded,
    system_income,
    order_id_b2p,
    idempotency_token,
    recipient_id,
    recipient_id_b2p,
    is_guest_commission,
    commission,
    guest_amount,
    recipient_amount,
    payment_type,
    status,
    status_b2p,
    review_id,
    updated_at,
    fail_reason,
    tips_link,
    card_pan,
    created_at,
    place_id,
    alias
) VALUES (
    '2e776108-3d51-4c8e-951d-4237015f3a41',NULL,50,NULL,'1.2.3.4',TRUE,10,NULL,FALSE,NULL,'431','idempotency_token_1','f907a11d-e1aa-4b2e-8253-069c58801727',
          '1',TRUE,3,50,47,'apple_pay_b2p','REGISTERED','REGISTERED','101','1970-01-31 03:03:01','','','','1970-01-31 03:03:00','','1'
),
(
    '2e776108-3d51-4c8e-951d-4237015f3a42',100,50,NULL,'1.2.3.4',TRUE,10,NULL,FALSE,NULL,NULL,'idempotency_token_2','',
          '',FALSE,0,0,0,'apple_pay_b2p','COMPLETED','COMPLETED','102','1970-01-31 00:03:01','','','','1970-01-31 00:03:00','',''
),
(
    '2e776108-3d51-4c8e-951d-4237015f3a43',NULL,50,NULL,'1.2.3.4',TRUE,10,NULL,FALSE,NULL,'432','idempotency_token_3','f907a11d-e1aa-4b2e-8253-069c58801727',
          '1',FALSE,0,50,50,'apple_pay_b2p','COMPLETED','COMPLETED','103','1970-01-31 03:03:01','','','','1970-01-31 03:03:00','','1'
),
(
    '2e776108-3d51-4c8e-951d-4237015f3a44',NULL,50,NULL,'1.2.3.4',TRUE,10,NULL,FALSE,NULL,'433','idempotency_token_4','f907a11d-e1aa-4b2e-8253-069c58801727',
          '1',TRUE,3,50,47,'google_pay_b2p','COMPLETED','COMPLETED','104','1970-01-31 03:03:01','','','','1970-01-31 03:03:00','','1'
),
(
    '2e776108-3d51-4c8e-951d-4237015f3a45',NULL,50,NULL,'1.2.3.4',TRUE,10,NULL,FALSE,NULL,'434','idempotency_token_5','f907a11d-e1aa-4b2e-8253-069c58801727',
          '1',TRUE,3,50,47,'yandex_pay_b2p','COMPLETED','COMPLETED','105','1970-01-31 03:03:01','','','','1970-01-31 03:03:00','','1'
),
(
    '2e776108-3d51-4c8e-951d-4237015f3a46',NULL,50,NULL,'1.2.3.4',TRUE,10,NULL,FALSE,NULL,'435','idempotency_token_6','f907a11d-e1aa-4b2e-8253-069c58801727',
          '1',TRUE,3,50,47,'b2p','COMPLETED','COMPLETED','106','1970-01-31 03:03:01','','','','1970-01-31 03:03:00','','1'
),
(
    '2e776108-3d51-4c8e-951d-4237015f3a47',NULL,50,NULL,'1.2.3.4',TRUE,10,NULL,FALSE,NULL,'436','idempotency_token_7','f907a11d-e1aa-4b2e-8253-069c58801727',
          '1',FALSE,0,50,50,'apple_pay_b2p','COMPLETED','COMPLETED','107','1970-01-31 02:00:01','','','','1970-01-31 02:00:00','','1'
)
;

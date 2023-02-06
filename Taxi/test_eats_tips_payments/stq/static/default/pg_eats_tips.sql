INSERT INTO eats_tips_payments.orders (
  order_id,
  yandex_user_id,
  amount,
  plus_amount,
  user_ip,
  user_has_plus,
  cashback_status,
  is_refunded,
  system_income
)
VALUES
(42, 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 110, 11, '1.2.3.4', false, 'in-progress', false, 600),
(43, 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 100, 10, '1.2.3.4', false, null, false, null),
(44, 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 120, 12, '1.2.3.4', false, 'in-progress', true, null),
(45, 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 130, 13, '1.2.3.4', false, 'failed', false, null),
(46, 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 140, 13, '1.2.3.4', false, 'in-progress', false, 0),
(47, 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 150, 13, '1.2.3.4', false, 'in-progress', false, null)
;

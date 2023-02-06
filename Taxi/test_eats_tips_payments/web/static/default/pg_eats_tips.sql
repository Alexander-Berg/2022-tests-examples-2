INSERT INTO eats_tips_payments.orders (
  order_id,
  id,
  yandex_user_id,
  recipient_id,
  amount,
  recipient_amount,
  plus_amount,
  status,
  created_at,
  place_id,
  user_has_plus,
  cashback_status
)
VALUES
(42, 'order000-0000-0000-0000-000000000042', 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 'f907a11d-e1aa-4b2e-8253-069c58801727', 110, 100, 11, 'COMPLETED', '2021-10-10 02:00:00', 'eef266b2-09b3-4218-8da9-c90928608d97', false, 'in-progress'),
(43, 'order000-0000-0000-0000-000000000043', 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 'f907a11d-e1aa-4b2e-8253-069c58801727', 100, 100, 10, 'COMPLETED', '2021-10-10 03:00:00', 'eef266b2-09b3-4218-8da9-c90928608d97', true, null),
(44, 'order000-0000-0000-0000-000000000044', 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 'f907a11d-e1aa-4b2e-8253-069c58801727', 120, 100, 12, 'COMPLETED', '2021-10-10 04:00:00', 'eef266b2-09b3-4218-8da9-c90928608d97', false, 'success'),
(45, 'order000-0000-0000-0000-000000000045', 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 'f907a11d-e1aa-4b2e-8253-069c58801727', 130, 100, 13, 'COMPLETED', '2021-10-10 05:00:00', 'eef266b2-09b3-4218-8da9-c90928608d97', false, 'failed'),
(46, 'order000-0000-0000-0000-000000000046', 'd45b09ec-6e5f-4e24-9e7e-fa293965d583', 'f907a11d-e1aa-4b2e-8253-069c58801727', 130, 100, 13, 'COMPLETED', '2021-10-10 06:00:00', 'eef266b2-09b3-4218-8da9-c90928608d97', false, null)
;

INSERT INTO eats_tips_payments.orders (
  order_id,
  id,
  amount,
  status,
  idempotency_token,
  card_pan,
  recipient_id
)
VALUES
(47, 'order000-0000-0000-0000-000000000047', 42, 'COMPLETED', 'token', 'bad card', 'f907a11d-e1aa-4b2e-8253-069c58801722'),
(48, 'order000-0000-0000-0000-000000000048', 43, 'COMPLETED', 'token2', 'normal card 1', 'f907a11d-e1aa-4b2e-8253-069c58801722'),
(49, 'order000-0000-0000-0000-000000000049', 44, 'COMPLETED', 'token3', 'normal card 1', 'f907a11d-e1aa-4b2e-8253-069c58801722')
;

INSERT INTO eats_tips_payments.blacklist_cards (
  pan
)
VALUES
('bad card')
;

INSERT INTO eats_tips_payments.reviews(
    review_id
    , recipient_id
    , recipient_type
    , place_id
    , review
    , star
    , quick_choices
    , idempotency_token
    , created_at
)
VALUES
('review00-0000-0000-0000-000000000044', 'f907a11d-e1aa-4b2e-8253-069c58801727', 'partner', 'eef266b2-09b3-4218-8da9-c90928608d97', 'Text review 44', 4, '{service}', 'idempotency_token_44', '2021-10-10 04:30:00Z'),
('review00-0000-0000-0000-000000000045', 'f907a11d-e1aa-4b2e-8253-069c58801727', 'partner', 'eef266b2-09b3-4218-8da9-c90928608d97', 'Text review 45', 4, '{}', 'idempotency_token_45', '2021-10-10 05:30:00Z'),
('review00-0000-0000-0000-000000000046', 'f907a11d-e1aa-4b2e-8253-069c58801727', 'partner', 'eef266b2-09b3-4218-8da9-c90928608d97', 'Text review 46', 5, '{}', 'idempotency_token_46', '2021-10-10 06:30:00Z')
;

INSERT INTO eats_tips_payments.orders_reviews(order_id, review_id)
VALUES
('order000-0000-0000-0000-000000000045', 'review00-0000-0000-0000-000000000045'),
('order000-0000-0000-0000-000000000046', 'review00-0000-0000-0000-000000000046')
;

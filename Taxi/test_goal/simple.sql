INSERT INTO persey_payments.fund
(
  fund_id,
  name,
  offer_link,
  operator_uid,
  balance_client_id,
  trust_partner_id,
  trust_product_id
)
VALUES
(
  'some_fund',
  'Имя фонда',
  'http://fund.com',
  '777',
  'some_client',
  'some_partner_id',
  'some_product_id'
);

INSERT INTO persey_payments.donation
(
  fund_id,
  sum,
  user_name,
  user_email,
  purchase_token,
  trust_order_id,
  status,
  city
)
VALUES
('some_fund', '123.45', 'aaa', 'bbb', 'ccc', 'ddd', 'started', 'Moscow'),
('some_fund', '543.21', 'aaa', 'bbb', 'ccc', 'ddd', 'finished', 'Moscow'),
('some_fund', '700000', 'aaa', 'bbb', 'ccc', 'ddd', 'finished', 'SPb')

INSERT INTO debt_collector.debts 
  (debt_id, metadata, service, 
   debtors, 
   created_at, updated_at, 
   version, idempotency_tokens,
   currency, debt, total,
   strategy_kind, strategy_installed_at, strategy_metadata,
   transactions_params,
   invoice_id, invoice_id_namespace, transactions_installation, originator,
   history, reason_code, reason_metadata)
VALUES ('with_two_debtors_id', '{"zone": "moscow"}', 'eats', 
        '{"taxi/phone_id/some_phone_id", "yandex/uid/some_uid"}', 
        '2021-03-08T00:00:00+00:00', '2021-03-09T00:00:00+00:00', 
        3, array['initial_token']::text[],
        'RUB', array[]::jsonb[], array[]::jsonb[],
	'null', '2021-01-01T00:00:00+00:00'::timestamptz, '{}'::jsonb,
	'{}'::jsonb,
	'with_two_debtors_invoice_id', NULL, 'eda', 'eats_payments',
        array[]::jsonb[], 'some_code', '{"from": "admin"}'),

       ('first_with_one_debtor_id', '{"zone": "moscow"}', 'eats', 
        '{"taxi/phone_id/some_phone_id"}', 
        '2021-03-08T00:00:00+00:00', '2021-03-09T00:00:00+00:00', 
        3, array[]::text[],
        'RUB', array[]::jsonb[], array[]::jsonb[],
        'null', '2021-01-01T00:00:00+00:00'::timestamptz, '{}'::jsonb,
	'{}'::jsonb,
        'first_with_one_debtor_invoice_id', NULL, 'eda', 'eats_payments',
        array[]::jsonb[], 'some_code', '{"from": "admin"}'),

       ('second_with_one_debtor_id', '{"zone": "moscow"}', 'eats', 
        '{"taxi/phone_id/some_phone_id"}', 
        '2021-03-08T00:00:00+00:00', '2021-03-09T00:00:00+00:00', 
        3, array[]::text[],
        'RUB', array[]::jsonb[], array[]::jsonb[],
        'null', '2021-01-01T00:00:00+00:00'::timestamptz, '{}'::jsonb,
	'{}'::jsonb,
        'second_with_one_debtor_invoice_id', NULL, 'eda', 'eats_payments',
        array[]::jsonb[], 'some_code', '{"from": "admin"}'),

       ('ignored_id', '{"zone": "moscow"}', 'eats', 
        '{"taxi/phone_id/ignored_phone_id"}', 
        '2021-03-08T00:00:00+00:00', '2021-03-09T00:00:00+00:00', 
        3, array[]::text[],
        'RUB', array[]::jsonb[], array[]::jsonb[],
        'null', '2021-01-01T00:00:00+00:00'::timestamptz, '{}'::jsonb,
	'{}'::jsonb,
        'ignored_invoice_id', NULL, 'eda', 'eats_payments',
        array[]::jsonb[], 'some_code', '{"from": "admin"}');


INSERT INTO debt_collector.debts_debtors (debtor, status, debt_id)
VALUES ('taxi/phone_id/some_phone_id', 'unpaid', 'with_two_debtors_id'),
       ('taxi/phone_id/some_phone_id', 'unpaid', 'first_with_one_debtor_id'),
       ('taxi/phone_id/some_phone_id', 'unpaid', 'second_with_one_debtor_id'),
       ('taxi/phone_id/ignored_phone_id', 'unpaid', 'ignored_id'),	
       ('yandex/uid/some_uid', 'unpaid', 'with_two_debtors_id'),
       ('yandex/uid/some_uid', 'paid', 'first_with_one_debtor_id');



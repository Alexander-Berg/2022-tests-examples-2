INSERT INTO debt_collector.debts 
  (debt_id, metadata, service, 
   debtors, 
   created_at, updated_at, 
   version, idempotency_tokens,
   payments,
   currency, debt, 
   total,
   strategy_kind, strategy_installed_at, strategy_metadata,
   transactions_params,
   invoice_id, invoice_id_namespace, transactions_installation, originator,
   history, reason_code, reason_metadata)
VALUES ('callback_debt_id', '{"zone": "moscow"}', 'eats', 
        '{"yandex/uid/some_uid"}', 
        '2021-03-08T00:00:00+00:00', '2021-03-09T00:00:00+00:00', 
        4, array['initial_token']::text[],
	array['{"type": "card", "method": "some_card_id"}']::jsonb[],
        'RUB', array['{"payment_type": "card", "items": [{"item_id": "food", "amount": "50.5"}, {"item_id": "water", "amount": "40"}, {"item_id": "bread", "amount": "20"}]}'::jsonb],
	array['{"payment_type": "card", "items": [{"item_id": "food", "amount": "100.5"}]}'::jsonb]::jsonb[],
	'time_table', '2021-01-01T00:00:00+00:00'::timestamptz, '{"schedule": ["2021-01-01T00:00:00.0+00:00"]}'::jsonb,
	'{}'::jsonb,
	'callback_debt_invoice_id', 'eda_namespace', 'eda', 'eats_payments',
        array['{"request": {"idempotency_token": "another_operation_id", "version": 2, "items_by_payment_type": {"total": [], "debt": [{"payment_type": "card", "items": [{"item_id": "food", "amount": "50.5"}, {"item_id": "water", "amount": "30"}, {"item_id": "bread", "amount": "40"}]}]}}}'::jsonb, '{"request": {"version": 3}}'::jsonb]::jsonb[], 'some_code', '{"from": "admin"}');

INSERT INTO debt_collector.debts_debtors (debtor, status, debt_id)
VALUES ('yandex/uid/some_uid', 'unpaid', 'callback_debt_id');



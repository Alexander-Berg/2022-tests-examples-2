insert into payouts.data_closed(
	process_uid,
	transaction_id,
	part_count,
	payout_batch_id,
	branch_type,
	firm_id,
	client_id,
	contract_id,
	contract_alias,
	currency,
	amount_w_vat,
	amount_w_vat_applied,
	amount_w_vat_saldo,
	netting_sign,
	accounting_date,
	accounting_period,
	payload,
	created_at_utc,
	updated_at_utc,
	person_id,
	dry_run
)
values
(
    'ffcf46d7d863493da5e5cbdca8b9adec',
    6222872,
	0,
	1,
	'expenses',
	13,
	'1349515601',
	'3697980',
	'ОФ-1553027/20',
	'RUB',
	13.78,
	13.78,
	0.00,
	1,
	'2022-03-20',
	'2022-03',
	'{"account_info": {"account": "ЛСТ-12345678"}}'::jsonb,
	'2022-03-03T01:17:41.119996'::timestamp,
	'2022-03-03T01:17:41.119996'::timestamp,
	'13489397',
	False
),
(
    '2f6bf8bea0c346b4a695be23d9a6ba03',
	6222877,
	0,
	2,
	'expenses',
	13,
	'1349547813',
	'3714633',
	'ОФ-1567291/20',
	'RUB',
	36.04,
	36.04,
	0.00,
	1,
	'2022-03-20',
	'2022-03',
   '{"account_info": {"account": "ЛСТ-12345678"}}'::jsonb,
   '2022-03-04T01:32:46.166692'::timestamp,
   '2022-03-04T01:32:46.166692'::timestamp,
   '13506136',
   False
),
(
    '2f6bf8bea0c346b4a695be23d9a6ba03',
	6222878,
	0,
	3,
	'expenses',
	13,
	'1349547813',
	'3714633',
	'ОФ-1567291/20',
	'RUB',
	36.04,
	36.04,
	0.00,
	1,
	'2022-03-20',
	'2022-03',
   '{"account_info": {"account": "ЛСТ-12345678"}}'::jsonb,
   '2022-03-04T01:32:46.166692'::timestamp,
   '2022-03-04T01:32:46.166692'::timestamp,
   '13506136',
    True
),
(
    '2f6bf8bea0c346b4a695be23d9a6ba03',
	6222879,
	0,
	3,
	'expenses',
	13,
	'1349547813',
	'3714633',
	'ОФ-1567291/20',
	'RUB',
	36.04,
	36.04,
	0.00,
	1,
	'2022-04-20',
	'2022-04',
   '{"account_info": {"account": "ЛСТ-12345678"}}'::jsonb,
   '2022-04-04T01:32:46.166692'::timestamp,
   '2022-04-04T01:32:46.166692'::timestamp,
   '13506136',
    True
);
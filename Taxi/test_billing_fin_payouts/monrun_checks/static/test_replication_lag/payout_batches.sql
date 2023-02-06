insert into payouts.payout_batches (
	batch_id,
    type_code,
    status_code,
    client_id,
    contract_id,
    contract_alias,
    contract_type,
    firm_id,
    person_id,
    amount_w_vat,
    currency,
    created_at_utc,
    updated_at_utc
)
values
(
	1,
    'PAYOUT',
    'EXPORT_READY',
    '123456',
    '654321',
    '654321/123',
    'revenues',
     13,
    '111111',
    1234.56,
    'RUB',
	'2022-06-21 09:59:03.0676',
	'2022-06-21 09:59:03.0676'
),
(
	2,
    'PAYOUT',
    'EXPORT_READY',
    '123457',
    '754321',
    '754321/123',
    'revenues',
    13,
    '222222',
    1234.57,
    'RUB',
	'2022-06-22 09:59:15.817547',
	'2022-06-22 09:59:15.817547'
),
(
	3,
    'PAYOUT',
    'EXPORT_READY',
    '123458',
    '854321',
    '854321/123',
    'revenues',
    13,
    '333333',
    1234.58,
    'RUB',
    '2022-06-23 09:59:32.015871',
    '2022-06-23 09:59:32.015871'
);



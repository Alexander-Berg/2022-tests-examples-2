INSERT INTO fees.draft_spec(id, change_doc_id) VALUES (2, 'some_random_change_doc_id');

INSERT INTO fees.base_rule (
    rule_id,
    tariff_zone, tariff, tag, payment_type,
    starts_at, ends_at, time_zone,
    rule_type, fee,
    min_order_cost, max_order_cost,
    billing_values,
    rates,
    cancellation_percent, expiration,
    branding_discounts,
    vat,
    changelog,
    draft_spec_id
) VALUES (
    'some_fixed_percent_commission_contract_id_in_future_end',
    'moscow', null, null, 'corp',
    '2018-12-31T20:00:00+03:00', '2030-01-01T00:00:00.789+03:00', 'Europe/Moscow',
    'fixed_percent', '{"percent": 1100}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000, "unrealized_rate": 105000}',
    null, '{"cost":8000000,"percent":1100}',
    '[]',
    11800,
    '[]',
    2
);

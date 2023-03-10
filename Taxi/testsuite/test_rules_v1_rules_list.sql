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
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000}',
    null, '{"cost":8000000,"percent":1100}',
    '[]',
    11800,
    '[]',
    2
), (
    'pool_htan_commission',
    'moscow', null, null, 'pool',
    '2017-09-12T14:05:00+0000', '2017-12-06T16:20:00+0000', 'Europe/Moscow',
    'pool_htan', '{"asymp":160000,"cost_norm":107107,"kc":4000,"ks":27000,"max_commission_percent":1600,"max_diff":2000000,"max_rel_profit":24000,"min_rel_profit":7700,"numerator":3741000
      }',
    0, 6000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":0,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":0,"extra_percent_with_rent":0,"max_age_in_seconds":0},"taximeter_payment":0}',
    0, '{"cost":8000000,"percent":1100}',
    '[]',
    11800,
    '[]',
    2
), (
    'some_absolute_value_commission_contract_id',
    'moscow', null, 'great_tag', 'cash',
    '2016-12-31T21:00:00+0000', '2017-12-31T21:00:00+0000', 'Europe/Moscow',
    'absolute_value', '{"cancel_commission":2000000,"commission":3000000,"expired_commission":1000000}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":0}',
    0, '{"cost":0,"percent":0}',
    '[]',
    11800,
    '[]',
    2
), (
    'some_fixed_percent_commission_contract_id',
    'moscow', null, null, 'cash',
    '2016-12-30T17:00:00+0000', '2017-12-31T21:00:00+0000', 'Europe/Moscow',
    'fixed_percent', '{"percent": 1100}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":39000}',
    null, '{"cost":8000000,"percent":1100}',
    '[]',
    11800,
    '[]',
    2
), (
    'some_fixed_percent_commission_contract_id_with_unlimited_end',
    'moscow', null, 'some_tag', 'cash',
    '2016-12-30T17:00:00+0000', null, 'Europe/Moscow',
    'fixed_percent', '{"percent": 1100}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000}',
    null, '{"cost":8000000,"percent":1100}',
    '[]',
    11800,
    '[]',
    2
), (
    'some_asymptotic_formula_commission_contract_id',
    'moscow', 'uberkids', null, 'cash',
    '2016-12-30T17:00:00+0000', '2017-12-30T21:00:00+0000', 'Europe/Moscow',
    'asymptotic_formula', '{"asymp":162000,"cost_norm":-393990,"max_commission_percent":1630,"numerator":8538000}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":5}',
    1100, '{"cost":8000000,"percent":1100}',
    '[{"marketing_level":["lightbox","co_branding","sticker"],"value":500}]',
    11800,
    '[]',
    2
);

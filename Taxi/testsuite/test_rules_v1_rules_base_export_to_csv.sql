INSERT INTO fees.draft_spec (id, change_doc_id, initiator)
VALUES (1234, 'earlier_draft', 'me');


INSERT INTO fees.base_rule (
    rule_id, draft_spec_id, tariff_zone, tariff, tag, payment_type,
    starts_at, ends_at, time_zone,
    rule_type,
    fee,
    min_order_cost, max_order_cost,
    billing_values,
    rates,
    cancellation_percent, expiration,
    branding_discounts,
    vat,
    changelog
) VALUES (
    'a_fixed_percent_rule', 1234, 'moscow', 'express', 'cargocorp_promo_tag', 'card',
    '2021-11-15T19:17:00+0300', '2029-12-31T12:00:00+0300', 'Europe/Moscow',
    'fixed_percent',
    '{"percent":7500}',
    0, 150000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":0,"u_min":0}',
    '{"acp":0,"agp":0,"callcenter_commission_percent":300,"hiring":{"extra_percent":0,"extra_percent_with_rent":0,"max_age_in_seconds":0},"taximeter_payment":55000}',
    7500, '{"cost":8000000,"percent":1100}',
    '[]',
    12000,
    '[{"end":null,"login":"me","ticket":"RUPRICE-1"}]'
), (
    'an_asympotic_rule_with_discounts', 1234, 'moscow', null, null, 'card',
    '2020-02-28T13:40:00+0300', null, 'Europe/Moscow',
    'asymptotic_formula',
    '{"asymp":160000,"cost_norm":107107,"max_commission_percent":1600,"numerator":3471000}',
    0, 150000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":0,"u_min":0}',
    '{"acp":2,"agp":1,"callcenter_commission_percent":300,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":55000}',
    null, '{"cost":8000000,"percent":1100}',
    '[{"marketing_level":["lightbox"],"value":300},{"marketing_level":["co_branding","lightbox"],"value":500},{"marketing_level":["sticker"],"value":600},{"marketing_level":["co_branding"],"value":500},{"marketing_level":["sticker","lightbox"],"value":600}]',
    12000,
    '[{"end":null,"login":"you","ticket":"RUPRICE-2"}]'
), (
    'not_active_already', 1234, 'moscow', null, null, 'card',
    '2020-01-01T00:00:00+0300', '2022-01-01T00:00:00+0300', 'Europe/Moscow',
    'asymptotic_formula',
    '{"asymp":160000,"cost_norm":107107,"max_commission_percent":1600,"numerator":3471000}',
    0, 150000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":0,"u_min":0}',
    '{"acp":2,"agp":1,"callcenter_commission_percent":300,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":550}',
    null, '{"cost":8000000,"percent":1100}',
    '[]',
    12000,
    '[{"end":null,"login":"you","ticket":"RUPRICE-2"}]'
), (
    'another_zone', 1234, 'minsk', null, null, 'card',
    '2020-02-28T13:40:00+0300', null, 'Europe/Moscow',
    'fixed_percent',
    '{"percent": 1500}',
    0, 150000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":0,"u_min":0}',
    '{"acp":2,"agp":1,"callcenter_commission_percent":300,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":550}',
    null, '{"cost":8000000,"percent":1100}',
    '[]',
    12000,
    '[{"end":null,"login":"you","ticket":"RUPRICE-2"}]'
);

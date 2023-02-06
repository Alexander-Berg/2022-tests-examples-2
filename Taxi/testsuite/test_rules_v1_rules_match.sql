INSERT INTO fees.draft_spec(
    id,
    change_doc_id
) VALUES (
    2,
    'zone1,zone2:some random change_doc_id'
), (
    3,
    'category_change_id'
), (
    4,
    'category_change_id1'
);

ALTER SEQUENCE fees.draft_spec_id_seq RESTART WITH 99;

INSERT INTO fees.category (
    id,
    draft_spec_id,
    name,
    description,
    kind,
    product,
    detailed_product,
    fields,
    starts_at,
    ends_at
) VALUES (
    '2abf162a-b607-11ea-998e-07e60204cbcf',
    3,
    'a122',
    'a122',
    'a122',
    'product',
    'detailed_product',
    'core',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
), (
    '2abf162a-b607-11eb-998e-07e60204cbcf',
    3,
    'Hiring',
    'Комиссия с парков за привлеченных водителей',
    'hiring_fee',
    '{hiring_tlog_products[hiring_type]}',
    '{hiring_tlog_detailed_products[hiring_type]}',
    'hiring',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
), (
    '2abf262a-b607-11eb-998e-07e60204cbcf',
    3,
    'fine',
    'fine',
    'fine',
    'fine_product',
    'fine_detailed_product',
    'fine',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
), (
    '0e6c8361-c186-4cc2-a3a0-e282b249a8ed',
    3,
    'Taximeter',
    'Оброк за таксометр',
    'taximeter',
    'order',
    'gross_taximeter_payment',
    'absolute',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
), (
    'ba8ee296-c6f2-410c-82b9-0033cc8ff7a2',
    3,
    'Acquiring',
    'Эквайринг',
    'acquiring',
    'card_trips_acquiring_commission',
    'gross_card_trips_acquiring_commission',
    'core',
    '2019-01-01T21:00:00+00:00',
    '2119-01-01T21:00:00+00:00'
)
;

INSERT INTO fees.category_account(
    category_id,
    agreement,
    sub_account,
    currency,
    entity
) VALUES (
    '2abf162a-b607-11ea-998e-07e60204cbcf',
    'taxi/yandex-ride',
    'sub_account',
    'order_currency',
    'entity'
), (
    '2abf162a-b607-11ea-998e-07e60204cbcf',
    'taxi/yandex-ride',
    'sub_account',
    'contract_currency',
    'entity'
);

INSERT INTO fees.rule(
    id,
    kind, -- description
    starts_at, ends_at, -- time
    tariff_zone, tariff, -- matcher
    draft_spec_id, -- draft section
    fees
) VALUES
(
    '2abf062a-b607-11ea-998e-07e60204cbcf',
    'software_subscription',
    '2017-01-02T00:00:00+00:00', '2120-01-01T21:00:00+00:00',
    'moscow', 'econom',
    2,
    ('[{"fee":"42.0001", "subscription_level": "some_level"}, ' ||
    ' {"fee":"400", "subscription_level": "some_level1"}]')::JSONB
),
(
    'f3a0503d-3f30-4a43-8e30-71d77ebcaa1f',
    'software_subscription',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', 'econom',
    2,
    '[{"fee":"42.0001", "subscription_level": "some_level"}]'
),
(
    'f3b0503e-3f30-4a43-8e30-71d77ebcaa1f',
    'software_subscription',
    '2017-01-02T00:00:00+00:00', '2120-01-01T21:00:00+00:00',
    'moscow', 'econom',
    2,
    '[{"fee":"42.0042", "subscription_level": "some_level"}]'
),
-- ryles with and without tag test
(
    'f3b0503d-3f30-4a43-8e30-71d77ebcaa1f',
    'a122',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', 'econom',
    2,
    '{"percent": "42"}'
),
(
    'f3b3503d-3f30-4a43-8e30-71d77ebcaa1f',
    'a122',
    '2024-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', 'econom',
    2,
    '{"percent": "-42"}'
),
-- most specific contract test (no tag, no tariff for one rule)
(
    'f3c3503d-3f30-4a43-8e30-71d77ebcaa1f',
    'a122',
    '2010-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', 'comfortplus',
    2,
    '{"percent": "-43"}'
),
(
    'f3d3503d-3f30-4a43-8e30-71d77ebcaa1f',
    'a122',
    '2010-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', '',
    2,
    '{"percent": "-44"}'
), (
    'f3d3503d-3f31-4a43-8e30-71d77ebcaa1f',
    'hiring_fee',
    '2020-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', '',
    2,
    '{"percent": "-12"}'
), (
    '1739fe24-a1a3-4fb0-9075-2d7802b23f00',
    'software_subscription',
    '2017-01-02T00:00:00+00:00', '2120-01-01T21:00:00+00:00',
    'spb', 'econom',
    2,
    ('[{"fee":"42.0001", "subscription_level": "some_level"}, ' ||
    ' {"fee":"400", "subscription_level": "some_level1"}]')::JSONB
), (
    'f3d3613d-3f31-4a43-8e30-71d77ebcaa1f',
    'fine',
    '2020-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'spb', '',
    2,
    '{"fee": "22"}'
), (
    'f3d3613d-3f31-4a43-8e31-71d77ebcaa1f',
    'taximeter',
    '2020-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'taximeter_test', '',
    2,
    '{"fee": "22", "unrealized_fee": "30"}'
), (
    'f3d3503d-3f30-4a43-8e30-72d77ebcaa1f',
    'a122',
    '2010-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'test', '',
    2,
    '{"percent": "-44"}'
), (
    'f3d3503d-3f30-4a43-8e30-73d77ebcaa1f',
    'a122',
    '2010-01-01T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'test', '',
    2,
    '{"percent": "-44"}'
), (
    '3f994c47-671d-4c86-b9b4-3dc88ae3da53',
    'hiring_fee',
    '2020-12-31T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'magadan', 'business',
    2,
    '{"percent": "0.02"}'
), (
    'd7a7d8ce-f3d1-4e46-9ba0-3582436137cb',
    'taximeter',
    '2020-12-31T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'igarka', '',
    2,
    '{"fee": "1"}'
), (
    '41de1cc8-bf10-4dfa-b2b1-ff6ce48ef92d',
    'taximeter',
    '2020-12-31T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'igarka', 'suv',
    2,
    '{"fee": "0.0"}'
), (
    'fd8b8df0-0e5b-4448-bce3-fea2978d8870',
    'acquiring',
    '2020-12-31T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'ukhta', '',
    2,
    '{"percent": "0.05"}'
), (
    'db6f28c4-15a2-4885-9257-445bf2649198',
    'acquiring',
    '2020-12-31T21:00:00+00:00', '2030-01-01T21:00:00+00:00',
    'ukhta', 'suv',
    2,
    '{"percent": "0.0"}'
);

INSERT INTO fees.rule_hiring_type(
    rule_id, hiring_type, hiring_age
) VALUES (
    'f3d3503d-3f31-4a43-8e30-71d77ebcaa1f', 'commercial_returned', 180
), (
    '3f994c47-671d-4c86-b9b4-3dc88ae3da53', 'commercial', 180
);

INSERT INTO fees.rule_tag(
    rule_id, tag
) VALUES (
    'f3b3503d-3f30-4a43-8e30-71d77ebcaa1f', 'tag'
), (
    -- software_subscription with_tag
    'f3b0503e-3f30-4a43-8e30-71d77ebcaa1f', 'tag'
), (
    '1739fe24-a1a3-4fb0-9075-2d7802b23f00', 'some'
);

INSERT INTO fees.withdraw_from_driver_account(
    enabled,
    rule_id
) VALUES (
    true,
    '2abf062a-b607-11ea-998e-07e60204cbcf'
);

INSERT INTO fees.rule_fine_code(
    rule_id,
    fine_code
) VALUES (
    'f3d3613d-3f31-4a43-8e30-71d77ebcaa1f',
    'fine!!!'
);

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
    'some_fixed_percent_commission_contract_id_spb',
    'spb', null, null, 'card',
    '2016-12-31T21:00:00+03:00', null, 'Europe/Moscow',
    'fixed_percent', '{"percent": 1100}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000, "unrealized_rate": 105000}',
    1100, '{"cost":8000000,"percent":1100}',
    '[]',
    11800,
    '[]',
    2
), (
    'some_asymptotic_formula_commission_contract_id',
    'moscow', 'econom', null, 'cash',
    '2016-12-30T21:00:00+00:00', '2017-12-30T21:00:00+00:00', 'Europe/Moscow',
    'asymptotic_formula', '{"asymp":162000,"cost_norm":-393990,"max_commission_percent":1630,"numerator":8538000}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000}',
    1100, '{"cost":8000000,"percent":1100}',
    '[{"marketing_level":["lightbox","co_branding","sticker"],"value":500}]',
    11800,
    '[]',
    2
), (
    'some_absolute_value_commission_contract_id',
    'moscow', 'econom', 'great_tag', 'cash',
    '2016-12-31T21:00:00+00:00', '2999-12-31T21:00:00+00:00', 'Europe/Moscow',
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
    'some_fixed_percent_with_unlimited_end_card',
    'moscow', null, null, 'card',
    '2016-12-31T20:00:00.0+03:00', null, 'Europe/Moscow',
    'fixed_percent', '{"percent": 1100}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000}',
    1000, '{"cost":8000000,"percent":1200}',
    '[]',
    11800,
    '[]',
    2
), (
    'some_fixed_percent_with_future_end_card',
    'moscow', 'econom', null, 'card',
    '2018-12-31T20:00:00.0+03:00', '2030-01-01T00:00:00.0+03:00', 'Europe/Moscow',
    'fixed_percent', '{"percent": 1100}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000}',
    null, '{"cost":8000000,"percent":1200}',
    '[]',
    11800,
    '[]',
    2
), (
    'some_fixed_percent_commission_contract_id_spb_with_tag',
    'spb', null, 'tag', 'card',
    '2016-12-31T21:00:00+03:00', null, 'Europe/Moscow',
    'fixed_percent', '{"percent": 1200}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000}',
    1100, '{"cost":8000000,"percent":1100}',
    '[]',
    11800,
    '[]',
    2
), (
    'some_fixed_percent_commission_contract_id_spb_cash',
    'spb', 'comfort', null, 'cash',
    '2016-12-31T21:00:00.0+03:00', null, 'Europe/Moscow',
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
    'some_fixed_percent_commission_contract_id_spb_with_tag_cash',
    'spb', null, 'tag', 'cash',
    '2016-12-31T21:00:00.0+03:00', null, 'Europe/Moscow',
    'fixed_percent', '{"percent": 1200}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000}',
    null, '{"cost":8000000,"percent":1100}',
    '[]',
    11800,
    '[]',
    2
), (
    'some_fixed_percent_commission_contract_id_ekb_cash',
    'ekb', 'comfort', null, 'cash',
    '2016-12-31T21:00:00.0+03:00', null, 'Europe/Moscow',
    'fixed_percent', '{"percent": 0}',
    0, 60000000,
    '{"bcd":300,"p_max":600,"p_min":420,"u_max":600,"u_min":120}',
    '{"acp":200,"agp":1,"callcenter_commission_percent":0,"hiring":{"extra_percent":200,"extra_percent_with_rent":400,"max_age_in_seconds":15552000},"taximeter_payment":10000}',
    null, '{"cost":8000000,"percent":1100}',
    '[]',
    11800,
    '[]',
    2
);

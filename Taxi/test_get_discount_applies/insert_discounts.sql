INSERT INTO corp_discounts.discounts(
    discount_name, discount_services, currency, country, legal_information, rule
) VALUES
(
    'fixed rule',
    array['eats2'::corp_discounts.handlers__service_v1, 'drive'::corp_discounts.handlers__service_v1],
    'RUB',
    'RUS',
    '<h1>Discount title</h1><p>Discount description</p>',
    '{"amount":"200","minimal_order_sum":"600","orders_count":1,"rule_class": "first_orders_fixed"}'::jsonb
)

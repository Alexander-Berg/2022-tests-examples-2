INSERT INTO corp_discounts.discounts(
    discount_name, discount_services, currency, country, legal_information, rule
) VALUES
(
    'discount',
    array['eats2'::corp_discounts.handlers__service_v1, 'drive'::corp_discounts.handlers__service_v1],
    'RUB',
    'RUS',
    '<h1>Discount title</h1><p>Discount description</p>',
    '{"percent":20,"max_discount":"200","minimal_order_sum":"600","max_orders":1,"rule_class":"first_orders_percent"}'::jsonb
),
(
    'bonus',
    array['eats2'::corp_discounts.handlers__service_v1, 'drive'::corp_discounts.handlers__service_v1],
    'RUB',
    'RUS',
    '<h1>New discount title</h1><p>Another discount description</p>',
    '{"percent":10,"max_discount":"200","max_amount_spent":"500","rule_class":"amount_spent_percent"}'::jsonb
)

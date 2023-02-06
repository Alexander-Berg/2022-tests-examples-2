INSERT INTO cashback.order_rates (order_id, rates)
VALUES
('order_id_1', '{
  "by_classes": [
    {
      "value": 0.1,
      "class": "econom",
      "max_absolute_value": 100
    }
  ]
}'::jsonb),
('order_id_2', '{
  "by_classes": [
    {
      "value": 0.2,
      "class": "vip"
    }
  ]
}'::jsonb),
('order_id_3', '{
  "by_classes": [
    {
      "value": 0.3,
      "class": "comfortplus"
    },
    {
      "value": 0.2,
      "class": "vip"
    }
  ]
}'::jsonb),
('order_id_4', '{
  "by_classes": [
    {
      "value": 0.3,
      "class": "econom"
    },
    {
      "value": 0.2,
      "class": "vip"
    }
  ]
}'::jsonb),
('order_id_possible_cashback', '{
  "by_classes": [
    {
      "value": 0.1,
      "class": "econom",
      "max_absolute_value": 100
    }
  ],
  "marketing_cashback": {
    "possible_cashback": {
        "value": 0.1,
        "max_absolute_value": 100
    }
  }
}'::jsonb),
('order_id_with_marketing_cashbacks', '{
  "by_classes": [
    {
      "value": 0.1,
      "class": "econom",
      "max_absolute_value": 100
    }
  ],
  "marketing_cashback": {
    "possible_cashback": {
        "value": 0.1,
        "max_absolute_value": 100
    },
    "some_new_cashback": {
        "value": 0.1,
        "max_absolute_value": 100,
        "enabled": true,
        "static_payload":  {
            "budget_owner": "portal",
            "campaign_name": "changing_cashback_go",
            "cashback_type": "transaction",
            "issuer": "marketing_experiment",
            "service_id": "124",
            "ticket": "NEWSERVICE-1689"
        }
    }
  }
}'::jsonb);


INSERT INTO cashback.events
  (id, external_ref, type, status, value, currency, created, yandex_uid, source)
VALUES
  ('event_id_1', 'order_id_1', 'charge', 'new', '50', 'RUB', '2019-08-15T12:00:00+0', 'yandex_uid_1', 'service'),
  ('event_id_2', 'order_id_1', 'charge', 'done', '200', 'RUB', '2019-08-15T13:00:00+0', 'yandex_uid_1', 'service'),
  ('event_id_3', 'order_id_1', 'withdraw', 'new', '30', 'RUB', '2019-08-15T14:00:00+0', 'yandex_uid_1', 'service'),
  ('event_id_4', 'order_id_2', 'withdraw', 'new', '11', 'RUB', '2019-08-15T15:00:00+0', 'yandex_uid_1', 'service'),
  ('event_id_5', 'order_id_3', 'charge', 'done', '11', 'RUB', '2019-08-15T16:00:00+0', 'yandex_uid_1', 'service');


INSERT INTO cashback.order_clears
    (order_id, service, value, currency, version, cashback_sum)
VALUES
    ('order_id_2', 'yataxi', '50', 'RUB', 2, '10'),
    ('order_id_6', 'lavka', '50', 'RUB', 6, '10');

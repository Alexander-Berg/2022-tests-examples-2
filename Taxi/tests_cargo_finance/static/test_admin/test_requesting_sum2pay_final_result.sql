INSERT INTO cargo_finance.pay_applying_state (
    flow,
    entity_id,
    created_at,
    last_modified_at,
    last_request_taken_at,
    requested_sum2pay,
    force_upsert,
    using_debt_collector,
    last_applying_created_at,
    applying_sum2pay,
    last_applying_modified_at,
    applying_result,
    last_final_result_modified_at,
    applied_sum2pay_revision,
    notification_revision,
    final_result,
    is_final_result_paid)
VALUES
    ('claims',
     '67d84b3e8e7043e4ab971f0ebe7c8ef3',
     '2022-02-04T11:30:00.861903+00:00',
     '2022-02-04T11:31:23.533171+00:00',
     '2022-02-04T11:31:09.798337+00:00',
     '{
        "taxi": {
          "taxi_order_id": "90a247425253cc249a702fa6fa5ddeea"
        },
        "client": {
          "agent": {
            "sum": "484",
            "context": {
              "city": "Москва",
              "park_clid": "400000269565",
              "park_dbid": "b9b29f9b54da4c1fb9e6868afde703d9",
              "customer_ip": "::ffff:109.173.64.38",
              "invoice_due": "2022-02-04T11:30:00.20949+00:00",
              "nearest_zone": "moscow",
              "tariff_class": "courier",
              "taxi_alias_id": "255b7def82a5cd1c97d1a6cf4bc42b98",
              "taxi_order_id": "90a247425253cc249a702fa6fa5ddeea",
              "corp_client_id": "d6e08f9487d046e88dd2c47e1c1817f7",
              "taxi_order_due": "2022-02-04T11:36:00+00:00",
              "billing_product": {
                "id": "400000269565_68934679_ride",
                "name": "ride"
              },
              "taxi_order_source": "cargo",
              "fiscal_receipt_info": {
                "vat": "nds_none",
                "title": "Услуги курьерской доставки",
                "personal_tin_id": "e192ea8963f14021aa5be83117eb62a8"
              },
              "contractor_profile_id": "0ddcad06dc3d4050a2e65b1529aec0bc"
            },
            "currency": "RUB",
            "payment_methods": {
              "card": {
                "cardstorage_id": "card-x8db0a21402c61fe132a1c5a7",
                "owner_yandex_uid": "36828704"
              }
            }
          }
        },
        "revision": 6,
        "is_service_complete": false
     }',
     false,
     false,
     null,
     null,
     null,
     null,
     '2022-02-04T11:31:23.533171+00:00',
     6,
     2,
     '{
        "client": {
            "agent": {
            "paid_sum": "484",
            "is_finished": true}
        }
      }',
     true);

INSERT INTO feeds_admin.recipient_group
    (feed_uuid, group_id, group_type, yql_link, group_settings)
VALUES
    (
        '11111111111111111111111111111111',
        10,
        'channels'::feeds_admin.recipient_group_type,
        NULL,
        '{"type": "tag"}'::jsonb
    );

INSERT INTO feeds_admin.recipients (recipient_id, group_id)
VALUES
    ('tag1', 10),
    ('tag2', 10);

INSERT INTO feeds_admin.schedule
    (
        schedule_id, recurrence, parameters
    )
VALUES
    (
        1,
        'once',
        '{
            "class_": "feeds_admin.models.schedule.Interval",
            "start_at": {
                "value": "2000-01-01T00:00:00+03:00",
                "class_": "datetime.datetime"
            },
            "finish_at": {
                "value": "3000-01-01T00:00:00+03:00",
                "class_": "datetime.datetime"
            }
        }'
    );


INSERT INTO feeds_admin.feeds
    (
        target_service,
        feed_uuid,
        schedule_id,
        name,
        settings,
        payload,
        status,
        author,
        ticket,
        created,
        updated
    )
VALUES
    (
        'contractor-marketplace',
        '11111111111111111111111111111111',
        1,
        'ContractorMarketplace',
        '{}'::jsonb,
        '{
          "slider": true,
          "slider_place_id": 50,
          "place_id": 50.2,
          "offer_id": "offer_id",
          "categories": [
            "auto_parts"
          ],

          "title": "Автозапчасти",
          "subtitle": {
            "keyset": "some_keyset",
            "key": "some_key"
          },
          "partner": {
            "name": "Партнёр",
            "media_id": "media_id"
          },
          "actions": [
            {
              "type": "link",
              "text": "Ссылка",
              "data": "link://somewhere"
            },
            {
              "type": "copy",
              "text": "Промокод",
              "data": "YANDEX"
            }
          ],
          "meta_info": {
            "extra_badge": {
              "message": {
                "keyset": "some_keyset",
                "key": "some_key"
              },
              "badge_color": "FFD4E0",
              "text_color": "D4120F"
            },
            "barcode_params": {
              "is_send_enabled": true,
              "type": "ean13"
            },
            "daily_per_driver_limit": 1,
            "expiration_params": {
              "image_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
              "tanker_key_header": "tanker_key_header",
              "tanker_key_subheader": "tanker_key_subheader",
              "is_timer_enabled": true
            },
            "promocode_params": {
              "text": {
                  "key": "some_key",
                  "keyset": "some_keyset"
              },
              "url": "https://decathlon.digift.ru/card/show/code/\\{\\}"
            },
            "individual_link_params": {
              "agreement_text": {
                "key": "some_key",
                "keyset": "some_keyset"
              },
              "link_caption": {
                  "key": "some_key",
                  "keyset": "some_keyset"
              },
              "general_link": "https://mango.rocks/",
              "individual_link": "https://mango.rocks/name=\\{name\\}&dbid_uuid=\\{dbid_uuid\\}"
            },
            "payment_link_template_params": {
              "link_caption": {
                  "key": "some_key",
                  "keyset": "some_keyset"
              },
              "payment_link_template": "https:://yandex.ru/?lat=\\{lat\\}&lon=\\{lon\\}&id=\\{payment_id\\}"
            },
            "total_per_driver_limit": 2,
            "total_per_unique_driver_limit": 3
          },
          "price": "29.9",
          "balance_payment": true
        }'::jsonb,
        'created',
        'adomogashev',
        'TAXICRM-1',
        '2019-12-30 00:00:00+0300'::timestamp with time zone,
        '2019-12-31 00:00:00+0300'::timestamp with time zone
    );

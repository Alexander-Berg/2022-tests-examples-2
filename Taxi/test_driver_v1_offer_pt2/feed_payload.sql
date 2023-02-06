INSERT INTO contractor_merch.feed_payloads_history(
    id,

    feed_id,
    locale,

    feed_payload,

    created_at
) VALUES (
    'payload_id1',

    'feed-id-1',
    'ru',

    '{
        "actions": [
          {
            "data": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "text": "Rick Astley",
            "type": "link"
          }
        ],
        "balance_payment": true,
        "categories": [
          "tire",
          "food"
        ],
        "category": "tire",
        "feeds_admin_id": "feeds-admin-id-1",
        "meta_info": {
          "expiration_params": {
            "is_timer_enabled": true,
            "tanker_key_header": "timer.tags.gold.blocked"
          },
          "extra_badge": {
            "badge_color": "FFD4E0",
            "message": "Expired",
            "text_color": "D4120F"
          },
          "priority_params": {
            "duration_minutes": 60,
            "tag_name": "gold"
          }
        },
        "name": "RRRR",
        "partner": {
          "name": "Apple"
        },
        "price": "200.0000",
        "title": "Title",
        "offer_id": "metric"
    }',

    '2021-05-01T14:00:00Z'::timestamptz
);

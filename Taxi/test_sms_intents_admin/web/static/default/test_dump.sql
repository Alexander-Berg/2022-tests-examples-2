INSERT INTO sms_intents_admin.intents (
    intent,
    status,
    info,
    technical,
    texts,
    created,
    updated
)
VALUES (
    'int_2000'::text,  -- intent
    'active'::sms_intents_admin.status,  -- status

    '{
        "business_group": "Ride-Hailing",
        "cost_center": "ride-hailing",
        "description": "Отправка SMS по тестированию на ковид",
        "meta_type": "Demand",
        "recipients_type": ["user", "general"],
        "responsible": ["v-belikov", "stasya-kh"],
        "is_marketing": true
    }'::json,

    '{
        "ignore_errors": ["limit_exceeded"],
        "mask_text": true,
        "message_ttl": 30,
        "notification_instead_sms": {
            "acknowledge_ttl": 30,
            "applications": ["android", "iphone"],
            "delivery_ttl": 20,
            "enabled": true,
            "payload_template_name": "taxi_default",
            "phone_type": "yandex",
            "send_only_if_has_notification": false
        },
        "pass_user_agent": false,
        "provider": {
            "is_sender_changeable": false,
            "name": "yasms",
            "sender": "yango",
            "settings": {
                "route": "taxi",
                "sender": "yango"
            }
        },
        "request_idempotency": {
            "enabled": true,
            "token_ttl": 1000
        },
        "use_fallback_queue": true,
        "use_whitelist": false
    }'::json,

    '{
        "allowed_translations": [
            {
                "key": "my_key",
                "keyset": "tanker"
            }
        ],
        "is_automatic": true
    }'::json,

    '2000-01-01 00:00:00+03'::timestamp with time zone,
    '2000-01-01 00:00:00+03'::timestamp with time zone
), (
    'int_2010'::text,  -- intent
    'archived'::sms_intents_admin.status,  -- status

    '{
        "business_group": "Ride-Hailing",
        "cost_center": "ride-hailing",
        "description": "Отправка SMS по тестированию на ковид",
        "meta_type": "Demand",
        "recipients_type": ["user", "general"],
        "responsible": ["v-belikov", "stasya-kh"],
        "is_marketing": true
    }'::json,

    '{
        "ignore_errors": ["limit_exceeded"],
        "mask_text": true,
        "message_ttl": 30,
        "notification_instead_sms": {
            "acknowledge_ttl": 30,
            "applications": ["android", "iphone"],
            "delivery_ttl": 20,
            "enabled": true,
            "payload_template_name": "taxi_default",
            "phone_type": "yandex",
            "send_only_if_has_notification": false
        },
        "pass_user_agent": false,
        "provider": {
            "is_sender_changeable": false,
            "name": "yasms",
            "sender": "yango",
            "settings": {
                "route": "taxi",
                "sender": "yango"
            }
        },
        "request_idempotency": {
            "enabled": true,
            "token_ttl": 1000
        },
        "use_fallback_queue": true,
        "use_whitelist": false
    }'::json,

    '{
        "allowed_translations": [
            {
                "key": "my_key",
                "keyset": "tanker"
            }
        ],
        "is_automatic": true
    }'::json,

    '2000-01-01 00:00:00+03'::timestamp with time zone,
    '2010-01-01 00:00:00+03'::timestamp with time zone
);

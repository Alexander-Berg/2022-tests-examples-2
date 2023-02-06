INSERT INTO promotions.promotions (
    id,
    revision,
    revision_history,
    name,
    name_tsv,
    promotion_type,
    created_at,
    updated_at,
    published_at,
    status,
    meta_tags,
    zones,
    screens,
    priority,
    starts_at,
    ends_at,
    experiment,
    has_yql_data,
    yql_data,
    pages,
    extra_fields) VALUES
(
    'e7deaabe0e0b4c9f8a86e19a6da4db59',
    null,
    null,
    'test_promo_compat',
    to_tsvector('test_promo_compat'),
    'fullscreen',
    '2021-02-11 14:40:27.849662',
    '2021-02-11 18:09:03.417863',
    null,
    'created',
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    ARRAY['NO_SCREEN']::TEXT[],
    1,
    null,
    null,
    null,
    false,
    null,
    '{
        "pages": [
            {
                "widgets": {
                    "close_button": {"color": "FFFFFF"},
                    "action_buttons": [
                        {
                            "text": "Some Text",
                            "color": "FFFFFF",
                            "deeplink": "https://some.host/path",
                            "text_color": "21201F"
                        }
                    ]
                },
                "backgrounds": ["promotion_92315518-e717-4d00-9472-a253e2cfa330"]
            }
        ]
    }'::jsonb,
    '{}'::jsonb
);

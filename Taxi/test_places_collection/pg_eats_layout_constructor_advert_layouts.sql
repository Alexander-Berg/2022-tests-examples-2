insert into constructor.widget_templates (
    type,
    name,
    meta,
    payload,
    payload_schema
)
values
(
    'places_collection',
    'Places list with ads and no yabs settings',
    '{
        "place_filter_type": "open",
        "output_type": "list",
        "advert_settings": {"ads_only": true}
    }'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places_collection',
    'Places list with ads and yabs settings',
    '{
        "place_filter_type": "open",
        "output_type": "list",
        "advert_settings": {
            "ads_only": true,
            "yabs_params": {
                "page_id": 1,
                "target_ref": "testsuite",
                "page_ref": "testsuite"
            }
        }
    }'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places_collection',
    'Places list with ads and yabs settings with coefs and no send_rel',
    '{
        "place_filter_type": "open",
        "output_type": "list",
        "advert_settings": {
            "ads_only": true,
            "yabs_params": {
                "page_id": 1,
                "target_ref": "testsuite",
                "page_ref": "testsuite",
                "coefficients": {
                    "yabs_ctr":  1,
                    "eats_ctr": 0,
                    "relevance_multiplier": 1
                }
            }
        }
    }'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places_collection',
    'Places list with ads and yabs settings with coefs and false send_rel',
    '{
        "place_filter_type": "open",
        "output_type": "list",
        "advert_settings": {
            "ads_only": true,
            "yabs_params": {
                "page_id": 1,
                "target_ref": "testsuite",
                "page_ref": "testsuite",
                "coefficients": {
                    "yabs_ctr":  1,
                    "eats_ctr": 0,
                    "send_relevance": false,
                    "relevance_multiplier": 1
                }
            }
        }
    }'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places_collection',
    'Places list with ads and yabs settings with coefs and true send_rel',
    '{
        "place_filter_type": "open",
        "output_type": "list",
        "advert_settings": {
            "ads_only": true,
            "yabs_params": {
                "page_id": 1,
                "target_ref": "testsuite",
                "page_ref": "testsuite",
                "coefficients": {
                    "yabs_ctr":  1,
                    "eats_ctr": 0,
                    "send_relevance": true,
                    "relevance_multiplier": 1
                }
            }
        }
    }'::jsonb,
    '{}'::jsonb,
    '{}'::jsonb
);

insert into constructor.layouts (
    name,
    slug,
    author
)
values
(
    'Layout with places with ads and without yabs settings',
    'layout_no_yabs_settings',
    'udalovmax'
),
(
    'Layout with places with ads and with yabs settings',
    'layout_yabs_settings',
    'udalovmax'
),
(
    'Layout with places with ads and with yabs settings and no send_rel',
    'layout_yabs_settings_no_send_rel',
    'udalovmax'
),
(
    'Layout with places with ads and with yabs settings and false send_rel',
    'layout_yabs_settings_false_send_rel',
    'udalovmax'
),
(
    'Layout with places with ads and with yabs settings and true send_rel',
    'layout_yabs_settings_true_send_rel',
    'udalovmax'
);

insert into constructor.layout_widgets (
    name,
    url_id,
    widget_template_id,
    layout_id,
    meta,
    payload
)
values
(
    'places',
    1,
    1,
    1,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places',
    2,
    2,
    2,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places',
    3,
    3,
    3,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places',
    4,
    4,
    4,
    '{}'::jsonb,
    '{}'::jsonb
),
(
    'places',
    5,
    5,
    5,
    '{}'::jsonb,
    '{}'::jsonb
);

INSERT INTO promotions.collections (id, name, name_tsv, cells)
VALUES (
    'default_collection_id',
    'default_collection_name',
    to_tsvector('default_collection_name'),
    (
        '{
            "cells": [
                {
                    "one_of": [
                        {"type": "scenario", "scenario": "afisha-event"},
                        {"type": "tag", "tag": "scooter"},
                        {"type": "promotion_id", "promotion_id": "id1"}
                    ],
                    "size": {"width": 4, "height": 4}
                }
            ]
        }'
    )::jsonb
), (
    'collection_id_1',
    'collection_name_1',
    to_tsvector('collection_name_1'),
    (
        '{
            "cells": [
                {
                    "one_of": [
                        {"type": "scenario", "scenario": "afisha-event"},
                        {"type": "tag", "tag": "scooter"},
                        {"type": "promotion_id", "promotion_id": "id1"}
                    ],
                    "size": {"width": 4, "height": 4}
                }
            ]
        }'
    )::jsonb
);

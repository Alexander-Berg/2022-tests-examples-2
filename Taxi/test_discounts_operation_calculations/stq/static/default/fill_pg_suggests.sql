INSERT INTO discounts_operation_calculations.suggests(
    id,
    algorithm_ids,
    author,
    discounts_city,
    draft_url,
    draft_id,
    status,
    created_at,
    updated_at,
    statistics,
    multidraft_params,
    budget,
    max_absolute_value,
    calc_segments_params,
    fixed_discounts
)
VALUES (1, ARRAY['kt'], 'test_user', 'test_city', null, null, 'CALC_SEGMENT_STATS', '2021-08-10 23:43:21', '2021-08-10 23:53:21', '[]', '{}', NULL, NULL,
'{"common_params": {"discounts_city": "test_city", "companies": ["company1", "company2"], "tariffs": ["uberx", "econom"], "payment_methods": ["card","bitkoin","cash"], "min_discount": 0, "max_discount": 40},
  "custom_params": [{"algorithm_id": "kt", "max_surge": 1.8, "with_push": true, "fallback_discount": 6}]}', '{}')
;

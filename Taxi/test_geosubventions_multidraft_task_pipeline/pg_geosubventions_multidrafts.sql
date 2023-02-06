INSERT INTO "operation_calculations"."geosubventions_multidrafts_info" (
    multidraft_id,
    task_id,
    tariff_zones,
    tariffs,
    multidraft_start,
	multidraft_end,
    current_rule_end,
    current_epxeriment_end,
	experiment_tags,
	polygons_name_mapping,
	tag_name_mapping,
    experiment_name
) VALUES
(
    1,
  '5f9b08b19da21d53ed964473',
   ARRAY['moscow'],
    ARRAY['econom'],
    '2020-10-17 11:31:41',
    '2020-10-18 12:31:41',
    '2020-10-18 12:31:41',
    '2020-10-18 12:31:41',
    ARRAY['1_test_tag_1', '1_test_tag_2'],
    '{"pol_1": "blabla_pol_1"}'::jsonb,
    '{"tag_1": "1_test_tag_1", "tag_2": "1_test_tag_2"}'::jsonb,
    '1_test_exp'
)
;

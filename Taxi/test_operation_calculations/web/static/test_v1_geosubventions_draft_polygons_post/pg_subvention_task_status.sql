INSERT INTO "operation_calculations"."subvention_tasks" (
    "id",
    "task",
    "creator",
    "experimental_conf"
) VALUES
(
    '7f9b08b19da21d53ed964474',
    '{"rush_hours": {"data": {}, "percentile": 0.65, "surge_pwr": 2.2, "distance_threshold": 0.3}, "polygons": {"data": [], "surge_weight_power": 1.3, "cost_weight_power": 0, "eps": 0.028, "min_samples": 1, "cluster_percent_of_sample": 0.03, "alpha_param": 0.007, "surge_threshold": 1.2}, "draft_rules": [], "data_loader": {"date_from": "2020-11-03 10:25:32", "date_to": "2020-11-17 10:25:32", "tariff_zones": ["moscow"], "tariffs": ["econom"]}, "budget": {"how_apply": "driver"}}'::jsonb,
    'amneziya',
    NULL
),
(
    '7f9b08b19da21d53ed964475',
    '{"rush_hours": {"data": {}, "percentile": 0.65, "surge_pwr": 2.2, "distance_threshold": 0.3}, "polygons": {"data": [], "surge_weight_power": 1.3, "cost_weight_power": 0, "eps": 0.028, "min_samples": 1, "cluster_percent_of_sample": 0.03, "alpha_param": 0.007, "surge_threshold": 1.2}, "draft_rules": [], "data_loader": {"date_from": "2020-11-03 10:25:32", "date_to": "2020-11-17 10:25:32", "tariff_zones": ["moscow"], "tariffs": ["econom"]}, "budget": {"how_apply": "driver"}}'::jsonb,
    'amneziya',
    NULL
),
(
    '7f9b08b19da21d53ed964476',
    '{"rush_hours": {"data": {}, "percentile": 0.65, "surge_pwr": 2.2, "distance_threshold": 0.3}, "polygons": {"data": [], "surge_weight_power": 1.3, "cost_weight_power": 0, "eps": 0.028, "min_samples": 1, "cluster_percent_of_sample": 0.03, "alpha_param": 0.007, "surge_threshold": 1.2}, "draft_rules": [], "data_loader": {"date_from": "2020-11-03 10:25:32", "date_to": "2020-11-17 10:25:32", "tariff_zones": ["moscow", "himki"], "tariffs": ["econom"]}, "budget": {"how_apply": "driver"}}'::jsonb,
    'amneziya',
    NULL
),
(
    '7f9b08b19da21d53ed964477',
    '{"rush_hours": {"data": {}, "percentile": 0.65, "surge_pwr": 2.2, "distance_threshold": 0.3}, "polygons": {"data": [], "surge_weight_power": 1.3, "cost_weight_power": 0, "eps": 0.028, "min_samples": 1, "cluster_percent_of_sample": 0.03, "alpha_param": 0.007, "surge_threshold": 1.2}, "draft_rules": [], "data_loader": {"date_from": "2020-11-03 10:25:32", "date_to": "2020-11-17 10:25:32", "tariff_zones": ["moscow", "himki"], "tariffs": ["uberx"]}, "budget": {"how_apply": "driver"}}'::jsonb,
    'amneziya',
    NULL
);

INSERT INTO "operation_calculations"."subvention_task_result" (
    "id",
    "data",
    "experimental_data"
) VALUES
(
    '7f9b08b19da21d53ed964474',
    '{"task_id": "7f9b08b19da21d53ed964474", "rush_hours": {"0": [{"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}]}, "polygons": [{"id": "5fb38a175e48dae578953b08_pol0", "type": "Feature", "properties": {"name": "my_existing_pol1", "existing": true}, "geometry": {"type": "Polygon", "coordinates": [[[50.28081572113459, 53.24089465235615], [50.28729095173748, 53.23952285175096], [50.2884903, 53.2391425], [50.28081572113459, 53.24089465235615]]]}}, {"id": "5fb38a175e48dae578953b08_pol1", "type": "Feature", "properties": {"name": "my_existing_pol2", "existing": true}, "geometry": {"type": "Polygon", "coordinates": [[[50.26784131007092, 53.25091179801678], [50.26857345576475, 53.24658996980415], [50.262743, 53.2340709996], [50.26784131007092, 53.25091179801678]]]}}, {"id": "5fb38a175e48dae578953b08_pol3", "type": "Feature", "properties": {"name": "my_existing_pol3", "existing": true}, "geometry": {"type": "Polygon", "coordinates": [[[50.077633, 53.178471], [50.07736569338627, 53.17848700187584], [50.076286, 53.178841], [50.077633, 53.178471]]]}}], "draft_rules": [{"categories": ["econom"], "rule_sum": 205, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol0"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}, {"categories": ["econom"], "rule_sum": 180, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol1"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}, {"categories": ["econom"], "rule_sum": 180, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol3"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}], "budget": [{"stats": {"5fb38a175e48dae578953b08_pol0": {"subv_cost": 25415.257562500003, "subv_cost_wo_surge": 62763.94302333359, "orders_cnt": 765.7205, "unique_drivers": 1.057625}, "5fb38a175e48dae578953b08_pol3": {"subv_cost": 25415.257562500003, "subv_cost_wo_surge": 62763.94302333359, "orders_cnt": 765.7205, "unique_drivers": 1.057625}, "5fb38a175e48dae578953b08_pol1": {"subv_cost": 12100.8164375, "subv_cost_wo_surge": 26588.15474967497, "orders_cnt": 429.9245625, "unique_drivers": 1.057625}}, "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}], "budget_summary": {"3": 37516.074}}'::jsonb,
    NULL
),
(
    '7f9b08b19da21d53ed964475',
    '{"task_id": "7f9b08b19da21d53ed964475", "rush_hours": {"0": [{"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}]}, "polygons": [{"id": "5fb38a175e48dae578953b08_pol0", "type": "Feature", "properties": {"name": "my_existing_pol1", "existing": true}, "geometry": {"type": "Polygon", "coordinates": [[[50.28081572113459, 53.44089465235615], [50.28229095173748, 53.23952285175096], [50.2884903, 53.2391425], [50.28081572113459, 53.24089465235615]]]}}, {"id": "5fb38a175e48dae578953b08_pol1", "type": "Feature", "properties": {"name": "my_existing_pol2", "existing": true}, "geometry": {"type": "Polygon", "coordinates": [[[50.26784131007092, 53.25091179801678], [50.26857345576475, 53.24658996980415], [50.262743, 53.2340709996], [50.26784131007092, 53.25091179801678]]]}}, {"id": "5fb38a175e48dae578953b08_pol3", "type": "Feature", "properties": {"name": "my_existing_pol3", "existing": true}, "geometry": {"type": "Polygon", "coordinates": [[[50.077633, 53.178471], [50.07736569338627, 53.17848700187584], [50.076286, 53.178841], [50.077633, 53.178471]]]}}], "draft_rules": [{"categories": ["econom"], "rule_sum": 205, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol0"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}, {"categories": ["econom"], "rule_sum": 180, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol1"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}, {"categories": ["econom"], "rule_sum": 180, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol3"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}], "budget": [{"stats": {"5fb38a175e48dae578953b08_pol0": {"subv_cost": 25415.257562500003, "subv_cost_wo_surge": 62763.94302333359, "orders_cnt": 765.7205, "unique_drivers": 1.057625}, "5fb38a175e48dae578953b08_pol3": {"subv_cost": 25415.257562500003, "subv_cost_wo_surge": 62763.94302333359, "orders_cnt": 765.7205, "unique_drivers": 1.057625}, "5fb38a175e48dae578953b08_pol1": {"subv_cost": 12100.8164375, "subv_cost_wo_surge": 26588.15474967497, "orders_cnt": 429.9245625, "unique_drivers": 1.057625}}, "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}], "budget_summary": {"3": 37516.074}}'::jsonb,
    NULL
),
(
    '7f9b08b19da21d53ed964476',
    '{"task_id": "7f9b08b19da21d53ed964476", "rush_hours": {"0": [{"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}]}, "polygons": [{"id": "5fb38a175e48dae578953b08_pol0", "type": "Feature", "properties": {"name": "pol0"}, "geometry": {"type": "Polygon", "coordinates": [[[50.28081572113459, 53.24089465235615], [50.28729095173748, 53.23952285175096], [50.2884903, 53.2391425], [50.28081572113459, 53.24089465235615]]]}}, {"id": "5fb38a175e48dae578953b08_pol1", "type": "Feature", "properties": {"name": "pol2"}, "geometry": {"type": "Polygon", "coordinates": [[[50.26784131007092, 53.25091179801678], [50.26857345576475, 53.24658996980415], [50.262743, 53.2340709996], [50.26784131007092, 53.25091179801678]]]}}, {"id": "5fb38a175e48dae578953b08_pol3", "type": "Feature", "properties": {"name": "pol1"}, "geometry": {"type": "Polygon", "coordinates": [[[50.077633, 53.178471], [50.07736569338627, 53.17848700187584], [50.076286, 53.178841], [50.077633, 53.178471]]]}}], "draft_rules": [{"categories": ["econom"], "rule_sum": 205, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol0"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}, {"categories": ["econom"], "rule_sum": 180, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol1"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}, {"categories": ["econom"], "rule_sum": 180, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol3"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}], "budget": [{"stats": {"5fb38a175e48dae578953b08_pol0": {"subv_cost": 25415.257562500003, "subv_cost_wo_surge": 62763.94302333359, "orders_cnt": 765.7205, "unique_drivers": 1.057625}, "5fb38a175e48dae578953b08_pol3": {"subv_cost": 25415.257562500003, "subv_cost_wo_surge": 62763.94302333359, "orders_cnt": 765.7205, "unique_drivers": 1.057625}, "5fb38a175e48dae578953b08_pol1": {"subv_cost": 12100.8164375, "subv_cost_wo_surge": 26588.15474967497, "orders_cnt": 429.9245625, "unique_drivers": 1.057625}}, "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}], "budget_summary": {"3": 37516.074}}'::jsonb,
    NULL
),
(
    '7f9b08b19da21d53ed964477',
    '{"task_id": "7f9b08b19da21d53ed964476", "rush_hours": {"0": [{"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}]}, "polygons": [{"id": "5fb38a175e48dae578953b08_pol0", "type": "Feature", "properties": {"name": "pol0"}, "geometry": {"type": "Polygon", "coordinates": [[[50.28081572113459, 53.24089465235615], [50.28729095173748, 53.23952285175096], [50.2884903, 53.2391425], [50.28081572113459, 53.24089465235615]]]}}, {"id": "5fb38a175e48dae578953b08_pol1", "type": "Feature", "properties": {"name": "pol2"}, "geometry": {"type": "Polygon", "coordinates": [[[50.26784131007092, 53.25091179801678], [50.26857345576475, 53.24658996980415], [50.262743, 53.2340709996], [50.26784131007092, 53.25091179801678]]]}}, {"id": "5fb38a175e48dae578953b08_pol3", "type": "Feature", "properties": {"name": "pol1"}, "geometry": {"type": "Polygon", "coordinates": [[[50.077633, 53.178471], [50.07736569338627, 53.17848700187584], [50.076286, 53.178841], [50.077633, 53.178471]]]}}], "draft_rules": [{"categories": ["econom"], "rule_sum": 205, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol0"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}, {"categories": ["econom"], "rule_sum": 180, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol1"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}, {"categories": ["econom"], "rule_sum": 180, "rule_type": "guarantee", "geoareas": ["5fb38a175e48dae578953b08_pol3"], "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}], "budget": [{"stats": {"5fb38a175e48dae578953b08_pol0": {"subv_cost": 25415.257562500003, "subv_cost_wo_surge": 62763.94302333359, "orders_cnt": 765.7205, "unique_drivers": 1.057625}, "5fb38a175e48dae578953b08_pol3": {"subv_cost": 25415.257562500003, "subv_cost_wo_surge": 62763.94302333359, "orders_cnt": 765.7205, "unique_drivers": 1.057625}, "5fb38a175e48dae578953b08_pol1": {"subv_cost": 12100.8164375, "subv_cost_wo_surge": 26588.15474967497, "orders_cnt": 429.9245625, "unique_drivers": 1.057625}}, "interval": {"start_dayofweek": 2, "start_time": "00:00", "end_dayofweek": 2, "end_time": "01:00"}}], "budget_summary": {"3": 37516.074}}'::jsonb,
    NULL
);

INSERT INTO operation_calculations.geosubventions_multidrafts_info(
    multidraft_id,
    task_id,
    tariff_zones,
    tariffs,
    multidraft_start,
    multidraft_end,
    current_rule_end,
    current_epxeriment_end,
    polygons_name_mapping
) VALUES
(100500, '7f9b08b19da21d53ed964478', '{"moscow", "himki"}', '{"uberx"}', '2021-01-01 04:05:06', '2022-01-01 04:05:06', '2022-01-01 04:05:06', '2022-01-01 04:05:06', '{"5fb38a175e48dae578953b08_pol0": "crazy_polygon", "5fb38a175e48dae578953b08_pol1": "dummy_polygon", "5fb38a175e48dae578953b08_pol3": "stupid_polygon"}'::jsonb);

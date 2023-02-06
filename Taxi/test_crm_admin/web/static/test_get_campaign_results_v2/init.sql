INSERT INTO crm_admin.campaign_results
(campaign_id, metric_order, json_data)
values
(51, 4, '{"hint": "\u041f\u043e\u043b\u043e\u0436\u0438\u0442\u0435\u043b\u044c\u043d\u043e\u0435 \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435 \u043e\u0437\u043d\u0430\u0447\u0430\u0435\u0442", "unit": "\u20bd", "grade": -2, "value": 44489.12736833631, "metric": "Profit", "is_final": true, "description": "\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u043a\u043e\u043c\u043c\u0443\u043d\u0438\u043a\u0430\u0446\u0438\u0438", "metric_order": 1, "recommendation": null, "secondary_unit": "\u20bd", "secondary_value": 4.351014901548783, "secondary_description": "\u0421\u0442\u043e\u0438\u043c\u043e\u0441\u0442\u044c \u043e\u0434\u043d\u043e\u0433\u043e \u043a\u043e\u043d\u0442\u0430\u043a\u0442\u0430", "statistical_significance": false}'::jsonb),
(51, 1, '{"hint": "hint 51_1", "unit": "unit 51_1", "grade": -2, "value": 51.1, "metric": "Profit", "is_final": true, "description": "description 51_1", "metric_order": 1, "recommendation": "recommendation 51_1", "secondary_unit": "secondary_unit 51_1", "secondary_value": 5.11, "secondary_description": "secondary_description 51_1", "statistical_significance": false}'::jsonb),
(51, 2, '{"hint": null, "unit": null, "grade": -2, "value": null, "metric": "\u041d\u0435\u0442 \u043c\u0435\u0442\u0440\u0438\u043a\u0438", "is_final": true, "description": "\u041d\u0435 \u0432\u044b\u0431\u0440\u0430\u043d\u0430 \u043e\u0441\u043d\u043e\u0432\u043d\u0430\u044f \u043c\u0435\u0442\u0440\u0438\u043a\u0430", "metric_order": 1, "recommendation": "analytics", "secondary_unit": null, "secondary_value": null, "secondary_description": null, "statistical_significance": false}'::jsonb),
(52, 5, '{"hint": "\u041c\u0435\u0442\u0440\u0438\u043a\u0430 \u0440\u0430\u0441\u0441\u0447\u0438\u0442\u044b\u0432\u0430\u0435\u0442\u0441\u044f \u0432 \u0442\u0435\u0447\u0435\u043d\u0438\u0435 4-\u0445 \u043d\u0435\u0434\u0435\u043b\u044c", "unit": "\u20bd", "grade": 0, "value": -1187872.9652388096, "metric": "GMV", "is_final": true, "description": "\u041f\u0440\u0438\u0440\u043e\u0441\u0442 \u043e\u0442\u043d\u043e\u0441\u0438\u0442\u0435\u043b\u044c\u043d\u043e \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u044f", "metric_order": 3, "recommendation": null, "secondary_unit": "\u20bd", "secondary_value": -116.17339513337991, "secondary_description": "GMV \u043d\u0430 \u043e\u0434\u0438\u043d \u043a\u043e\u043d\u0442\u0430\u043a\u0442", "statistical_significance": false}'::jsonb);

-- TODO: Надо добавить группы с данными, группы без данных, кампанию с результататми,
--  но без групп (в реальности такого быть не должно, но проверить поведение надо)
insert into crm_admin.segment
(id, yql_shared_url, yt_table, control, created_at)
values
(511, 'yql_shared_url', 'yt_table', 0.00, '2021-01-19T10:00:00+03:00'),
(521, 'yql_shared_url', 'yt_table', 0.00, '2021-01-19T10:00:00+03:00')
;

insert into crm_admin.campaign
(id, segment_id, name, entity_type, trend, discount, state, owner_name, created_at, efficiency)
values
-- campaign with groups, 1 no stats, 1 empty stats, 2 with data
(51, 511, 'name', 'user', 'trend', false, 'FINISHED', 'stasnam', '2021-01-19T10:00:00+03:00', true),
-- campaign without groups
(52, 521, 'name', 'user', 'trend', false, 'FINISHED', 'stasnam', '2021-01-19T10:00:00+03:00', false)
;

insert into crm_admin.group
(id, segment_id, sending_stats, params, created_at, updated_at)
values
(
    1,
    511,
    NULL,
    '{"name": "gr1", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 100, "total": 300, "promo.fs": 200}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    2,
    511,
    '{}',
    '{"name": "gr2", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 100, "total": 300, "promo.fs": 200}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    3,
    511,
    '{"sent": 50, "failed": 40, "planned": 100, "skipped": 10, "finished_at": "2021-01-19T10:00:00+03:00"}',
    '{"channel": "SMS", "state": "EFFICIENCY_ANALYSIS", "name": "gr3", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 100, "total": 300, "promo.fs": 200}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
),
(
    4,
    511,
    '{"sent": 10, "failed": 10, "planned": 50, "skipped": 30, "finished_at": "2021-01-19T10:00:00+03:00"}',
    '{"channel": "SMS", "state": "EFFICIENCY_ANALYSIS", "name": "gr3", "limit": 0, "cities": [], "locales": [], "computed": {"PUSH": 400, "total": 900, "promo.fs": 500}}',
    '2021-01-19T10:00:00+03:00',
    '2021-01-19T10:00:00+03:00'
)
;

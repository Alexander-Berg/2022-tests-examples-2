INSERT INTO logistic_supply_conductor.slot_quotas (siblings_group_id, week_day, quota)
VALUES (1, 'wednesday', 1001), (1, 'friday', 1002), (1, 'sunday', 1003);

INSERT INTO logistic_supply_conductor.slot_quota_refs (quota_id, siblings_group_ref_id)
VALUES ('af31c824-066d-46df-0001-100000000001', 1), ('af31c824-066d-46df-0001-100000000002', 2), ('af31c824-066d-46df-0001-100000000003', 3)

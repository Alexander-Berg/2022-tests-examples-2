INSERT INTO logistic_supply_conductor.geoarea_refs (origin_id)
VALUES(('logistic_supply','first')), (('logistic_supply','second'));

INSERT INTO logistic_supply_conductor.stored_geoareas (ref_id, "polygon", boundary_box)
VALUES (1, '((42,50),(42,52),(40,52),(40,50),(42,50))', '((40,52),(42,50))'),
       (2, '((54,62),(54,64),(52,64),(52,62),(54,62))', '((52,64),(54,62))');

INSERT INTO
      logistic_supply_conductor.workshift_rule_version_stored_geoareas (workshift_rule_version_id, stored_geoarea_id)
VALUES(1,2),(2,1),(3,2);

INSERT INTO logistic_supply_conductor.workshift_slots
    (workshift_slot_id, workshift_rule_version_id, stored_geoarea_id,
    siblings_group_id, week_day, time_start, time_stop, quota_ref_id)
VALUES
(
    '76a3176e-f759-44bc-8fc7-43ea091bd68b',
    3,
    2,
    1,
    'wednesday',
    '2033-04-06T08:00:00Z',
    '2033-04-06T20:00:00Z',
    1
),
(
    'a278134c-49f2-48bc-b9b6-941c76650508',
    3,
    2,
    1,
    'friday',
    '2033-04-08T08:00:00Z',
    '2033-04-08T20:00:00Z',
    1
),
(
    '2bb2deea-7892-4d47-a43b-b9bf2a99f5b3',
    3,
    2,
    1,
    'sunday',
    '2033-04-10T08:00:00Z',
    '2033-04-10T20:00:00Z',
    1
);

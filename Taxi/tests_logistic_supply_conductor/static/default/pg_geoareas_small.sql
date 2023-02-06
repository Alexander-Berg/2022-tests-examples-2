INSERT INTO logistic_supply_conductor.geoarea_refs (origin_id)
VALUES(('logistic_supply','second'));

INSERT INTO logistic_supply_conductor.stored_geoareas (ref_id, "polygon", boundary_box)
VALUES
(
      1,
      '((54,62),(54,64),(52,64),(52,62),(54,62))'::POLYGON,
      '((52,64),(54,62))'::BOX
);

INSERT INTO
      logistic_supply_conductor.workshift_rule_version_stored_geoareas (workshift_rule_version_id, stored_geoarea_id)
SELECT
      id, 1
FROM
      logistic_supply_conductor.workshift_rule_versions;

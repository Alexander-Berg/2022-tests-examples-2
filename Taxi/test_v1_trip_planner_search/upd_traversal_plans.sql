UPDATE state.route_views
SET traversal_plan = ROW(ARRAY[]::db.traversal_plan_point[])::db.traversal_plan;

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(1, 'acfff773-398f-4913-b9e9-03bf5eda25ac', TRUE)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ac' IN (SELECT booking_id
                                                 FROM state.passengers);

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(1, 'acfff773-398f-4913-b9e9-03bf5eda25ad', TRUE)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ad' IN (SELECT booking_id
                                                 FROM state.passengers);

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(1, NULL, NULL)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ac' NOT IN (SELECT booking_id
                                                 FROM state.passengers) AND
      'acfff773-398f-4913-b9e9-03bf5eda25ad' NOT IN (SELECT booking_id
                                                 FROM state.passengers);

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(2, 'acfff773-398f-4913-b9e9-03bf5eda25ac', FALSE)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ac' IN (SELECT booking_id
                                                 FROM state.passengers);

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(2, NULL, NULL)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ac' NOT IN (SELECT booking_id
                                                 FROM state.passengers);

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(4, 'acfff773-398f-4913-b9e9-03bf5eda25ad', FALSE)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ad' IN (SELECT booking_id
                                                 FROM state.passengers);

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(4, NULL, NULL)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ad' NOT IN (SELECT booking_id
                                                 FROM state.passengers);

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(6, 'acfff773-398f-4913-b9e9-03bf5eda25ae', TRUE)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ae' IN (SELECT booking_id
                                                     FROM state.passengers);

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(6, NULL, NULL)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ae' NOT IN (SELECT booking_id
                                                 FROM state.passengers);

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(8, 'acfff773-398f-4913-b9e9-03bf5eda25ae', FALSE)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ae' IN (SELECT booking_id
                                                     FROM state.passengers);

UPDATE state.route_views
SET traversal_plan = ROW((traversal_plan).plan || ARRAY[(8, NULL, NULL)::db.traversal_plan_point])::db.traversal_plan
WHERE 'acfff773-398f-4913-b9e9-03bf5eda25ae' NOT IN (SELECT booking_id
                                                 FROM state.passengers);
